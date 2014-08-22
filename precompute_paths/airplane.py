from position import *

class Airplane(Position):
    MAX_RANGE = 50

    def __init__(self, json_data, arena):
        Position.__init__(self, json_data)
        self.path = None  # to be set by airways.update()
        self.path_idx = -1 # pointer to current position on path
        self.update(json_data)
        self.dest = json_data['resolved_dest']
        self.dest_name = json_data['dest']
        # 0 means low speed (moves when clock % 2 == 0); 1 means high speed (moves when clock % 1 == 0)
        self.speed = 2 if self.id.istitle() else 1
        self.start = arena.find_start(self)

    def update(self, json_data):
        self.x = json_data['x']
        self.y = json_data['y']
        self.z = json_data['alt']
        self.dir = json_data['dir'] * 45
        self.fuel = json_data['fuel']
        print "UPDATE airplane " + str(self)
        
    def __str__(self):
        return str(self.id) + ': [' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ';' + str(self.dir) + ';fuel=' + str(self.fuel) + ',path_idx=' + str(self.path_idx) + ']'

    def setTargetDirection(self):
        print 'b'

    def setTargetAltitude(self):
        print 'c'
