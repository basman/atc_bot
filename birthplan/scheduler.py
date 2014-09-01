import string
import copy
import time
from position import Airplane, Airport, Exit, Position

class Scheduler:
    # used for several flight paths improvements (i.e. pass above 3000 feet in the area of airports)
    COLLISION_RANGE = 4
    
    def __init__(self, arena, connector):
        self._arena = arena
        self._connector = connector
        self._schedules = {} # nested dict; _schedules[time][airplane_id] = position
    
    def _compute_commands(self, path, airplane):
        # compute commands along the path
        delta_z = 0 # ascent rate
        delta_z_idx = -1 # start of ascent rate
        for i in range(1, len(path)):
            speed = airplane.speed
            if i == 1:
                # slow plane might be born at odd time, so we might need a command on the first position (i.e. starting from airports)
                speed = 1
            
            # slow planes move every second time step
            if path[i].time % speed != 0:
                continue

            if path[i].z - path[i - speed].z != delta_z:
                if delta_z_idx >= 0:
                    path[delta_z_idx].add_cmd_altitude(path[i - speed].z) # new delta_z
                delta_z = path[i].z - path[i - speed].z
                if delta_z != 0:
                    delta_z_idx = i - speed
                    # don't forget last step (e.g. landing on airport)
                    if i == len(path) - 1:
                        path[i - speed].add_cmd_altitude(path[i].z)
                else:
                    delta_z_idx = -1
            if (i > 1 or path[0].z != 7) and path[i].dir != path[i - speed].dir or i == 1 and path[0].z == 7 and path[i].dir != path[0].reverseDirection():
                path[i - speed].add_cmd_direction(path[i].dir)

    def _complex_path(self, airplane):
        # used for airplanes were brute force path computation took to long
        raise Exception("emergency procedures necessary for airplane " + str(airplane))

    def _compute_path(self, airplane, timelimit):
        
        #print "looking for a path from " + str(start) + " to " + str(dest) + ", starting at " + str(p)

        begin_computation = time.time()

        start = Position(airplane)
        start.time = self._arena.clock
        plan = [ start ]
        
        # aim for approach position, one step in front of airport or exit
        tmp = Position(airplane.dest)
        tmp.dir = tmp.reverseDirection()
        if isinstance(airplane.dest, Airport):
            approach = tmp.step(0, 1)
        else:
            approach = tmp.step(0, 0)
        approach.dir = airplane.dest.dir # turn around
        approach.dir_tolerance = 90 # allow max. 90 degree derivation from target direction
            
        # enter recursion
        if not self._step_recursive(airplane, plan, start, approach, timelimit):
            print "Path of " + str(airplane) + " from " + str(start) + " to " + str(airplane.dest) + ": COMPUTATION TIMEOUT (comp.time=" + \
            str(int((time.time()-begin_computation) * 1000000)/1000.0) + "ms)"
            return False
            
        # append destination itself
        d = Position(airplane.dest)
        d.time = plan[-1].time + 1
        plan.append( d )
        
        self._compute_commands(plan, airplane)
            
        print "Path of " + str(airplane) + " from " + str(start) + " to " + str(airplane.dest) + " (" + str(len(plan)) + " steps, comp.time=" + \
        str(int((time.time()-begin_computation) * 100000)/100.0) + "ms): ",
        print string.join(map(str, plan), '; ')

        # add schedule to database
        for s in plan:
            if s.time < self._arena.clock:
                raise Exception("can't schedule for past time " + str(s.time) + ". current time: " + str(self._arena.clock))
            if not s.time in self._schedules:
                self._schedules[s.time] = {}
            self._schedules[s.time][airplane] = s
        
        return True

    def _scheduled_is_collision(self, airplane, p):
        if p.time in self._schedules:
            for a in self._schedules[p.time]:
                if self._schedules[p.time][a].is_collision(p):
                    return True
        return False

    def _step_recursive(self, airplane, path, p, dest, timeout):
        # slow planes move every second time step
        if (p.time+1) % airplane.speed != 0:
            p = copy.deepcopy(p)
            p.time += 1
            
            if self._scheduled_is_collision(airplane, p):
                return False
            
            path.append(p)
            if not self._step_recursive(airplane, path, p, dest, timeout):
                del(path[-1])
                return False
            else:
                return True
        
        if p.equals(dest):
            return True
        
        if len(path) > airplane.fuel * airplane.speed:
            return False
        
        if time.time() > timeout:
            #print "Airplane " + str(airplane) + " can't find a path before next update"
            return False
        
        #self.log += "\n   _step_recursive: try " + str(p)
        
        # to deal with existing airplanes, maintain direction and altitude for 
        # a while (if coming from an exit)
        if path[0].z > 0 and len(path) <= 2:
            steps = [ p.step() ]
        else:
            steps = self._gen_possible_steps(p, dest)
        
        possible_steps = {}
        
        # try to walk in any direction (preferrably towards dest)
        for s in steps:
            s.time = p.time+1
            
            if self._scheduled_is_collision(airplane, s):
                continue

            skip = False
            if s.equals(dest):
                # present arrival as only solution
                possible_steps[0] = [s]
                break
                
            # exclude illegal steps (out of area or invalid altitude) 
            if ( s.x <= 0 or s.y <= 0 or s.y >= self._arena.height-1 or s.x >= self._arena.width-1 or s.z < 1 or s.z > 9):
                continue
            # must start straight from airport
            if path[0].z == 0 and len(path) < 2 and s.dir != path[0].dir:
                continue
            # must be at altitude 9 if approaching any exit
            for e in self._arena.exits:
                if e.distanceXY(path[0]) > self.COLLISION_RANGE and \
                e.distanceXY(s) < self.COLLISION_RANGE and \
                s.z < 9:
                    skip = True
                    break
            for a in self._arena.airports:
                # except for our own destination: pass airports at 3000 feet or above
                if a.distanceXY(dest) > self.COLLISION_RANGE and \
                a.distanceXY(path[0]) > self.COLLISION_RANGE and \
                a.distanceXY(s) < self.COLLISION_RANGE and \
                s.z < 3:
                    skip = True
                    break

            if skip:
                continue

            distance = dest.distance(s)

            if not distance in possible_steps:
                possible_steps[distance] = []
            possible_steps[distance].append(s)
            
        if len(possible_steps) == 0:
            #print "  step_rec.: fail"
            return False
            
        ordered_steps = []
        for d in sorted(possible_steps):
            ordered_steps.extend(possible_steps[d])
            
        for st in ordered_steps:
            path.append(st)
            if self._step_recursive(airplane, path, st, dest, timeout):
                return True
            else:
                del(path[-1])
        return False
    
    def _gen_possible_steps(self, pos, dest):
        steps = []
        
        if pos.z == 0:
            steps.append(Position(pos))   # stay at airport or ...
            steps.append(pos.step(0, 1))  # ...take off
        else:
            for delta_dir in ( 0, -45, 45, -90, 90 ):
                for delta_z in (-1, 0, 1):
                    npos = pos.step(delta_dir, delta_z)
                    # skip invalid steps and enforce outgoing airplanes to approach an exit at 9000 feet
                    if not npos is None and not ( npos.z != 9 and isinstance(dest, Exit) and dest.distance(npos) < self.COLLISION_RANGE ):
                        steps.append(npos)
        return steps
    
    def update(self):
        # cleanup past schedule
        if self._arena.clock-1 in self._schedules:
            del(self._schedules[self._arena.clock-1])
            
        # Prio 0: guide old planes
        commands = []
        unguided = []
        for aid in sorted(self._arena.airplanes.keys()):
            a = self._arena.airplanes[aid]
            if self._arena.clock in self._schedules and a in self._schedules[self._arena.clock]:
                # only airplanes still on the ground can avoid this loop
                # (i.e. no collision free launch is possible at the moment)
                for c in self._schedules[self._arena.clock][a].cmd:
                    commands.append(a.id + c + "\n")
                    print "cmd: " + a.id + c

            # check flight path position for each plane
                if not a.equals(self._schedules[self._arena.clock][a]):
                    print "Path: " + self._sched2str(a)
                    raise Exception("airplane left flight path: " + str(a) + ", expected " + str(self._schedules[self._arena.clock][a]) + ', t=' + str(self._arena.clock))
            else:
                unguided.append(a)
            
        if len(commands) > 0:
            self._connector.send(string.join(commands))
            commands = []

        waiting = {}
        # allow searching for a solution for almost one update interval of atc
        timelimit = time.time() + self._arena.update_time - 0.2
        for a in unguided:
        # Prio 1: guide new planes in the air
            if a.z > 0:
                if not self._arena.clock in self._schedules or not a in self._schedules[self._arena.clock]:
                    # new airplane already in flight
                    if not self._compute_path(a, timelimit):
                        self._complex_path(a)
            
            else:
        # Prio 2: guide new planes waiting on the ground
                ap = a.start
                # pull up one single airplane per airport
                if not ap in waiting and not ap.must_wait(self._arena.clock):
                    waiting[ap] = a
                
                if not self._arena.clock in self._schedules or not a in self._schedules[self._arena.clock]:
                    self._compute_path(a, timelimit)
            
            # send commands for freshly routed planes
            if self._arena.clock in self._schedules and a in self._schedules[self._arena.clock]:
                for c in self._schedules[self._arena.clock][a].cmd:
                    commands.append(a.id + c + "\n")
                    print "cmd: " + a.id + c
        
        if len(commands) > 0:
            self._connector.send(string.join(commands))

    
    def _sched2str(self, airplane):
        clock = self._arena.clock
        result = ''
        while clock in self._schedules and airplane in self._schedules[clock]:
            if clock != self._arena.clock:
                result += ', '
            result += str(self._schedules[clock][airplane])
            clock += 1
        return result