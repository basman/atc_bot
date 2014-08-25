import json
from position import *

class Arena:
    def __init__(self, arena_json):
        self.exits = []
        self.airports = []
        self.destinations = {}
        self.beacons = []
        self.lines = []
        self.airplanes = {}
        self.parseJSON(arena_json)

    def parseJSON(self, arena_json):
        print "Arena.parseJSON: " +  arena_json
        arena_data = json.loads(arena_json)
        self.width = arena_data['width']
        self.height = arena_data['height']
        self.interval = arena_data['interval']
        self.clock = arena_data['clock']

        for e in arena_data['exits']:
            ex = Exit(e)
            self.exits.append(ex)
            self.destinations['E' + str(len(self.exits)-1)] = ex
            
        for a in arena_data['airports']:
            airpt = Airport(a)
            self.airports.append(airpt)
            self.destinations['A' + str(len(self.airports)-1)] = airpt
            
        for b in arena_data['beacons']:
            self.beacons.append(Beacon(b))

        for l in arena_data['lines']:
            self.lines.append(Line(l))
            
        for p in arena_data['airplanes']:
            p['resolved_dest'] = self.lookup_destination(p['dest'])
            a = Airplane(p, self)
            self.airplanes[a.id] = a
            
    def lookup_destination(self, name):
        assert name in self.destinations
        return self.destinations[name]
    
    def update(self, upd_json):
        new_planes = []
        airplane_data = json.loads(upd_json)
        self.clock = airplane_data['clock']
        plane_ids_found = {}
        for aplane_json in airplane_data['airplanes']:
            plane_ids_found[aplane_json['id']] = 1
            
            if aplane_json['id'] in self.airplanes:
                # update existing plane
                self.airplanes[aplane_json['id']].update(aplane_json)
            else:
                # new plane
                aplane_json['resolved_dest'] = self.lookup_destination(aplane_json['dest'])
                a = Airplane(aplane_json, self)
                self.airplanes[a.id] = a
                new_planes.append(a)
                
        # cleanup planes that are gone
        delete_planes = []
        for p in self.airplanes.keys():
            if not p in plane_ids_found:
                delete_planes.append(p)
        for p in delete_planes:
            del(self.airplanes[p])
            
        return new_planes
    
    def find_start(self, airplane):
        if airplane.z == 0:
            for airport in self.airports:
                if airport.equalsXY(airplane):
                    return airport
            else:
                raise Exception("no start airport found for grounded airplane: " + str(airplane))
        else:
            for e in self.exits:
                if e.equalsXY(airplane):
                    return e
        #raise Exception("could not find start of plane " + str(airplane))
        return None