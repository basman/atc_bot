from connector import Connector
from arena import Arena
from airways import Airways
import string

if __name__ == '__main__':
    try:
        con = Connector()
    except IOError as err:
        print "Error: connection failed"
        exit(1)
    
    buf = con.read() # read arena
    arena = Arena(buf)
    airways = Airways(arena)
    
    while True:
        commands = airways.update()
        if not commands is None and len(commands) > 0:
            con.send(string.join(commands))
        
        buf = con.read()
        new_planes = arena.update(buf)
        # set airplane.path
        airways.set_paths(new_planes)
