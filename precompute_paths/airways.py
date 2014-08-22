import string
from airplane import Airplane
from position import *

class Airways:
    # range within collisions of airways are accepted (flightplans need to deal with it by delaying airplanes)
    COLLISION_RANGE = 4
    
    def __init__(self, arena):
        self.arena = arena
        self.airways = []
        self.airways_by_ends = {}
        #self.compute_airways()
        self.set_paths(self.arena.airplanes.values())
    
    def compute_airways(self):
        destinations = self.arena.exits
        destinations.extend(self.arena.airports)
    
        count = 0
        for dest1 in destinations:
            for dest2 in destinations:
                if dest1 is dest2:
                    continue
                path = self.compute_path(dest1, dest2)
                self.airways.append(path)
                if not dest1 in self.airways_by_ends:
                    self.airways_by_ends[dest1] = {}
                self.airways_by_ends[dest1][dest2] = path
                count += 1
        print "computed " + str(count) + " flight paths"

    def compute_path(self, start, dest):
        p = Position(start)
        if isinstance(start, Exit):
            p.z = 7
            p.dir = p.reverseDirection()
    
        self.log = ""
        #print "looking for a path from " + str(start) + " to " + str(dest) + ", starting at " + str(p)

        path = [ Position(start) ]
        # planes enter at altitude 7
        if isinstance(start, Exit):
            path[0].z = 7
            path[0].dir = path[0].reverseDirection()
        
        # aim for approach position, one step in front of airport or exit
        tmp = Position(dest)
        tmp.dir = tmp.reverseDirection()
        if isinstance(dest, Airport):
            approach = tmp.step(0, 1)
        else:
            approach = tmp.step(0, 0)
        approach.dir = dest.dir
        approach.dir_tolerance = 90 # allow max. 90 degree derivation from target direction
            
        # enter recursion
        if not self.step_recursive(path, p, start, approach):
            print self.log
            print "Fatal: could not find a path from " + str(start) + " to " + str(dest)
            exit(1)
        
        # append destination itself, or path would end at approach position
        path.append(dest)
        
        # compute commands along the path
        delta_z = 0 # ascent rate
        delta_z_idx = -1 # start of ascent rate
                 
        for i in range(1,len(path)):
            if path[i].z - path[i-1].z != delta_z:
                if delta_z_idx >= 0:
                    path[delta_z_idx].add_cmd_altitude(path[i-1].z)
                
                # new delta_z
                delta_z = path[i].z - path[i-1].z
                
                if delta_z != 0:
                    delta_z_idx = i-1
                    # don't forget last step (e.g. landing on airport)
                    if i == len(path)-1:
                        path[i-1].add_cmd_altitude(path[i].z)
                else:
                    delta_z_idx = -1
            
            if (i > 1 or not isinstance(start, Exit)) and path[i].dir != path[i-1].dir or \
                i == 1 and isinstance(start, Exit) and path[i].dir != start.reverseDirection():
                path[i-1].add_cmd_direction(path[i].dir)
            
        print str(start) + " to " + str(dest) + " (" + str(len(path)) + " steps): ",
        print string.join(map(str, path), '; ')

        return path

    def step_recursive(self, path, p, start, dest):
        if p.equals(dest):
            return True
        
        if len(path) > Airplane.MAX_RANGE:
            return False
        
        #self.log += "\n   step_recursive: try " + str(p)
        
        # to deal with existing airplanes, maintain direction and altitude for 
        # a while after entering through an exit
        if not isinstance(start, Airport) and not isinstance(start, Exit) and len(path) <= 2:
            steps = [ p.step() ]
        else:
            steps = self.gen_possible_steps(p, start, dest)
        
        possible_steps = {}
        
        # try to walk in any direction (preferrably towards dest)
        for s in steps:
            if s.equals(dest):
                # present arrival as only solution
                possible_steps[0] = [s]
                break
            else:
                # exclude illegal steps (out of area or invalid altitude) 
                if ( s.x <= 0 or s.y <= 0 or s.y >= self.arena.height-1 or s.x >= self.arena.width-1 or s.z < 1 or s.z > 9):
                    continue
                # must start straight from airport
                if isinstance(start, Airport) and len(path) < 2 and s.dir != start.dir:
                    continue
                # must be at altitude 9 if approaching any exit
                for e in self.arena.exits:
                    if e.distanceXY(s) < self.COLLISION_RANGE and s.z < 9:
                        continue
                for a in self.arena.airports:
                    # except for our own destination: pass airports at 3000 feet or above
                    if a.distanceXY(dest) > 2 and a.distanceXY(s) < self.COLLISION_RANGE and s.z < 3:
                        continue

#             collision = False
#             for flightp in self.airways:
#                 if collision:
#                     break
#                 for other_s in flightp:
#                     if s.is_collision(other_s):
#                         if dest.distance(s) > self.COLLISION_RANGE and start.distance(s) > self.COLLISION_RANGE:
#                             collision = True
#                             break
#             if not collision:
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
            if self.step_recursive(path, st, start, dest):
                return True
            else:
                del(path[-1])
        return False
    
    
    def gen_possible_steps(self, pos, start, dest):
        steps = []
        for delta_dir in ( 0, -45, 45, -90, 90 ):
            for delta_z in (-1, 0, 1):
                # keep incoming planes at 7000 feet for a while or they will crash with outgoing planes
                if delta_z != 0 and isinstance(start, Exit) and start.distance(pos) < self.COLLISION_RANGE:
                    continue
                npos = pos.step(delta_dir, delta_z)
                # skip invalid steps and enforce outgoing airplanes to approach an exit at 9000 feet
                if not npos is None and not ( npos.z != 9 and isinstance(dest, Exit) and dest.distance(npos) < self.COLLISION_RANGE ):
                    steps.append(npos)
        return steps
    
    def update(self):
        commands = []
        
        waiting = {}
        for a in self.arena.airplanes.values():
            
            if self.arena.clock % a.speed != 0:
                continue # ignore slow planes

            # pull up one single airplane per airport
            if a.z == 0:
                ap = a.start
                if not ap in waiting:
                    waiting[ap] = a
                
                path = self.airways_by_ends[a.start][a.dest]
                
                for c in path[0].cmd:
                    commands.append(a.id + c + "\n")
            
            else:
            # find airways position for each plane, collect commands
                if a.path is None:
                    raise Exception("airplane has no path: " + str(a))
                for i in range(a.path_idx if a.path_idx >= 0 else 0, len(a.path)):
                    if a.path[i].equals(a):
                        a.path_idx = i
                        for c in a.path[a.path_idx].cmd:
                            commands.append(a.id + c + "\n")
                        break
                else:
                    print "Path: " + string.join(map(str, a.path), ',')
                    raise Exception("airplane left flight path: " + str(a) + ", expected " + (str(a.path[a.path_idx]) if a.path_idx >= 0 else '[?]'))
        
        for c in commands:
            print "cmd: " + c,
        return commands
    
    def set_paths(self, airplanes):
        for a in airplanes:
            if a.start is None:
                # guide plane already on route individually
                a.start = Position(a)
                a.path = self.compute_path(a.start, a.dest)
                print "Airplane " + str(a) + " uses individual flight path from " + str(a.start) + " to " + str(a.dest)
            else:
                if not a.start in self.airways_by_ends:
                    self.airways_by_ends[a.start] = {}
                if not a.dest in self.airways_by_ends[a.start]:
                    self.airways_by_ends[a.start][a.dest] = self.compute_path(a.start, a.dest)
                print "Airplane " + str(a) + " uses standard flight path from " + str(a.start) + " to " + str(a.dest)
                a.path = self.airways_by_ends[a.start][a.dest]
