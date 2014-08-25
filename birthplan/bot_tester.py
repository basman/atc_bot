from arena import Arena
from scheduler import Scheduler
import time

if __name__ == '__main__':
    try:
        fil = open("/home/rha/projects/atc/test-json/initial3.json", 'r')
        buf = ""
        while True:
            line = fil.readline()
            if line == "":
                break
            buf += line
        fil.close()
        
    except IOError as err:
        print "Error: reading file failed"
        exit(1)
    
    start_time = time.time()
    
    #buf = con.read() # read arena
    arena = Arena(buf)
    mid_time = time.time()
    sched = Scheduler(arena)
    
    stop_time = time.time()
    
    print "reading the arena took " + str(mid_time-start_time) + " seconds"
    print "computing flight paths took " + str(stop_time - mid_time) + " seconds"
    
    '''
    while True:
        buf = con.read()
        commands = arena.update(buf)
        if len(commands) > 0:
            con.send(commands)
    '''