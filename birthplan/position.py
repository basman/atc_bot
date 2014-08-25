import math
import string

class Position:
    dir_cmd = {  0: 'w',
                45: 'e',
                90: 'd',
                135: 'c',
                180: 'x',
                225: 'z',
                270: 'a',
                315: 'q' }
    
    def __init__(self, *args):
        self.dir_tolerance = 0
        self.cmd = []
        
        if len(args) == 1:
            if isinstance(args[0], dict):
                self.__init_json(*args)
            elif isinstance(args[0], Position):
                self.__init_copy(*args)
            else:
                raise TypeError("Error: unknown object type given to constructor of Position")
        elif len(args) >= 4 and len(args) <= 5:
            self.__init_values(*args)
        else:
            raise TypeError("Error: invalid number of arguments given to constructor of Position")
        
    def __init_copy(self, orig):
        self.__init_values(orig.x, orig.y, orig.z, orig.dir, orig.dir_tolerance)
    
    def __init_json(self, json):
        self.id = json['id']
        self.x = json['x']
        self.y = json['y']
        self.z = -1
        self.dir = json['dir'] * 45
    
    def __init_values(self, x, y, z, direction, direction_tolerance=0):
        self.x = x
        self.y = y
        self.z = z
        self.dir = direction
        self.dir_tolerance = direction_tolerance
    
    def equals(self, pos):
        if self.x == pos.x and self.y == pos.y and self.z == pos.z:
            # negative direction value means +-90 degrees tolerance
            if pos.dir_tolerance > 0:
                if self.dir >= 360 - pos.dir_tolerance and pos.dir <= pos.dir_tolerance:
                    if 360 - self.dir + pos.dir <= pos.dir_tolerance:
                        return True
                elif pos.dir >= 360 - pos.dir_tolerance and self.dir <= pos.dir_tolerance:
                    if 360 - pos.dir + self.dir <= pos.dir_tolerance:
                        return True
                elif abs(self.dir - pos.dir) <= pos.dir_tolerance:
                    return True
            elif self.dir == pos.dir:
                return True
        return False
    
    def equalsXY(self, pos):
        return self.x == pos.x and self.y == pos.y

    def step(self, delta_dir=0, delta_z=0):
        # compute and return a copy object obeying the given change in direction and altitude
        # delta_dir is in the range of -90 to 90
        # delta_z is in the range of -1 to 1
        if delta_z < -1 or delta_z > 1:
            raise ValueError("invalid delta_z value: " + str(delta_z))
        
        if delta_dir < -90 or delta_dir > 90 or delta_dir % 45 != 0:
            raise ValueError("invalid delta_dir value: " + str(delta_dir))
        
        if delta_z + self.z < 0 or delta_z + self.z > 9:
            return None
        
        npos = Position(self)
        
        npos.z += delta_z
        
        npos.dir = (npos.dir + delta_dir) % 360
        if npos.dir > 0 and npos.dir < 180:
            npos.x += 1
        elif npos.dir > 180:
            npos.x -= 1
        if npos.dir > 270 or npos.dir < 90:
            npos.y -= 1
        elif npos.dir > 90 and npos.dir < 270:
            npos.y += 1
        
        return npos
    
    def add_cmd_altitude(self, new_z):
        self.cmd.append('a' + str(new_z))

    def add_cmd_direction(self, new_dir):        
        self.cmd.append('t' + Position.dir_cmd[new_dir])
    
    def is_collision(self, pos):
        dx = abs(self.x - pos.x)
        dy = abs(self.y - pos.y)
        dz = abs(self.z - pos.z)
        if dx > 1 or dy > 1 or dz > 1:
            return False
        else:
            return True
        
    def distance(self, pos):
        #return max( abs(self.x-pos.x), abs(self.y-pos.y), abs(self.z-pos.z) )
        return math.sqrt( (self.x-pos.x)**2 + (self.y-pos.y)**2 + (self.z-pos.z)**2 )        
    
    def distanceXY(self, pos):
        #return max( abs(self.x-pos.x), abs(self.y-pos.y) )
        return math.sqrt( (self.x-pos.x)**2 + (self.y-pos.y)**2 )
    
    def reverseDirection(self):
        # compute the opposite direction
        return (self.dir + 180) % 360
    
    def __str__(self):
        return self._tostr()
    
    def _tostr(self):
        s = "[" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ';' + str(self.dir) 
        if len(self.cmd) > 0:
            s += ';' + string.join(self.cmd, ',')
        s += "]"
        return s
        
class Exit(Position):
    def __init__(self, *args):
        Position.__init__(self, *args)
        self.z = 9
        self.dir = self.reverseDirection()
        
    def __str__(self):
        return "E" + str(self.id) + self._tostr()
        
class Airport(Position):
    
    LAUNCH_INTERVAL = 5
    
    def __init__(self, *args):
        Position.__init__(self, *args)
        self.z = 0
        self.wait_until = -1

    def must_wait(self, clock):
        if self.wait_until < clock:
            self.wait_until = clock + self.LAUNCH_INTERVAL
            return False
        return True

    def __str__(self):
        return "A" + str(self.id)  + self._tostr()

class Beacon(Position):
    def __init__(self, *args):
        Position.__init__(self, *args)
        self.z = -1

    def __str__(self):
        return "B" + str(self.id) + self._tostr()

class Line:
    def __init__(self, json):
        self.id = json['id']
        self.x1 = json['x1']
        self.y1 = json['y1']
        self.x2 = json['x2']
        self.y2 = json['y2']


class Airplane(Position):
    MAX_RANGE = 50

    def __init__(self, json_data, arena):
        Position.__init__(self, json_data)
        self.update(json_data)
        self.dest = json_data['resolved_dest']
        self.dest_name = json_data['dest']
        # 0 means low speed (moves when clock % 2 == 0); 1 means high speed (moves when clock % 1 == 0)
        self.speed = 2 if self.id.istitle() else 1
        self.start = arena.find_start(self)
        Airplane.MAX_RANGE = arena.width + arena.height

    def update(self, json_data):
        self.x = json_data['x']
        self.y = json_data['y']
        self.z = json_data['alt']
        self.dir = json_data['dir'] * 45
        self.fuel = json_data['fuel']
        print "UPDATE airplane " + str(self)
        
    def __str__(self):
        return str(self.id) + ': [' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ';' + str(self.dir) + ';fuel=' + str(self.fuel) + ']'
