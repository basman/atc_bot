import string
from position import Airplane, Airport, Exit, Position
import copy

class Scheduler:
    # used for several flight paths improvements (i.e. pass above 3000 feet in the area of airports)
    COLLISION_RANGE = 4
    
    def __init__(self, arena):
        self.arena = arena
        self.schedules = {} # nested dict; schedules[time][airplane_id] = position
    

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

    def _compute_path(self, airplane):
        
        #print "looking for a path from " + str(start) + " to " + str(dest) + ", starting at " + str(p)

        start = Position(airplane)
        start.time = self.arena.clock
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
        if not self._step_recursive(airplane, plan, start, approach):
            if start.z == 0:
                return # airplane is waiting on ground. we might find a path later
            raise Exception("Fatal: could not find a path for " + str(airplane) + " from " + str(start) + " to " + str(airplane.dest))
            
        
        # append destination itself
        d = Position(airplane.dest)
        d.time = plan[-1].time + 1
        plan.append( d )
        
        self._compute_commands(plan, airplane)
            
        print str(start) + " to " + str(airplane.dest) + " (" + str(len(plan)) + " steps): ",
        print string.join(map(str, plan), '; ')

        # add schedule to database
        for s in plan:
            if s.time < self.arena.clock:
                raise Exception("can't schedule for past time " + str(s.time) + ". current time: " + str(self.arena.clock))
            if not s.time in self.schedules:
                self.schedules[s.time] = {}
            self.schedules[s.time][airplane] = s


    def _scheduled_is_collision(self, airplane, p):
        if p.time in self.schedules:
            for a in self.schedules[p.time]:
                if self.schedules[p.time][a].is_collision(p):
                    return True
        return False

    def _step_recursive(self, airplane, path, p, dest):
        # slow planes move every second time step
        if (p.time+1) % airplane.speed != 0:
            p = copy.deepcopy(p)
            p.time += 1
            
            if self._scheduled_is_collision(airplane, p):
                return False
            
            path.append(p)
            if not self._step_recursive(airplane, path, p, dest):
                del(path[-1])
                return False
            else:
                return True
        
        if p.equals(dest):
            return True
        
        if len(path) > Airplane.MAX_RANGE:
            return False
        
        #self.log += "\n   _step_recursive: try " + str(p)
        
        # to deal with existing airplanes, maintain direction and altitude for 
        # a while after entering through an exit
        if path[0].z > 0 and len(path) <= 2:
            steps = [ p.step() ]
        else:
            steps = self._gen_possible_steps(p, dest)
        
        possible_steps = {}
        
        # try to walk in any direction (preferrably towards dest)
        for s in steps:
            s.time = p.time+1
            
            skip = False
            if s.equals(dest):
                # present arrival as only solution
                possible_steps[0] = [s]
                break
            else:
                if self._scheduled_is_collision(airplane, s):
                    continue
                
                # exclude illegal steps (out of area or invalid altitude) 
                if ( s.x <= 0 or s.y <= 0 or s.y >= self.arena.height-1 or s.x >= self.arena.width-1 or s.z < 1 or s.z > 9):
                    continue
                # must start straight from airport
                if path[0].z == 0 and len(path) < 2 and s.dir != path[0].dir:
                    continue
                # must be at altitude 9 if approaching any exit
                for e in self.arena.exits:
                    if e.distanceXY(path[0]) > self.COLLISION_RANGE and \
                    e.distanceXY(s) < self.COLLISION_RANGE and \
                    s.z < 9:
                        skip = True
                        break
                for a in self.arena.airports:
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
            if self._step_recursive(airplane, path, st, dest):
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
        if self.arena.clock-1 in self.schedules:
            del(self.schedules[self.arena.clock-1])
            
        commands = []
        
        waiting = {}
        for a in self.arena.airplanes.values():
            
            # pull up one single airplane per airport
            if a.z == 0:
                ap = a.start
                if not ap in waiting and not ap.must_wait(self.arena.clock):
                    waiting[ap] = a
                
                if not self.arena.clock in self.schedules or not a in self.schedules[self.arena.clock]:
                    self._compute_path(a)
                
            else:
            # check flight path position for each plane, collect commands
                if not self.arena.clock in self.schedules or not a in self.schedules[self.arena.clock]:
                    # new airplane already in flight
                    self._compute_path(a)
                if not a.equals(self.schedules[self.arena.clock][a]):
                    print "Path: " + self._sched2str(a)
                    raise Exception("airplane left flight path: " + str(a) + ", expected " + str(self.schedules[self.arena.clock][a]) + ', t=' + str(self.arena.clock))

            if self.arena.clock in self.schedules and a in self.schedules[self.arena.clock]:
                # only airplanes still on the ground can avoid this loop
                # (i.e. no collision free launch is possible at the moment)
                for c in self.schedules[self.arena.clock][a].cmd:
                    commands.append(a.id + c + "\n")
        
        for c in commands:
            print "cmd: " + c,
        return commands
    
    def _sched2str(self, airplane):
        clock = self.arena.clock
        result = ''
        while clock in self.schedules and airplane in self.schedules[clock]:
            if clock != self.arena.clock:
                result += ', '
            result += str(self.schedules[clock][airplane])
            clock += 1
        return result