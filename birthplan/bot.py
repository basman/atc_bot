from connector import Connector
from arena import Arena
from scheduler import Scheduler
import string

if __name__ == '__main__':
    try:
        con = Connector()
    except IOError as err:
        print "Error: connection failed"
        exit(1)
    
    buf = con.read() # read arena
    arena = Arena(buf)
    sched = Scheduler(arena, con)
    
    while True:
        sched.update()
        
        buf = con.read()
        new_planes = arena.update(buf)

