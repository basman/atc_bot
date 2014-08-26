from arena import Arena
from scheduler import Scheduler
import time
import string
import os

if __name__ == '__main__':
    dir = '/home/rha/projects/atc/test-json/collision2'
    start_time = time.time()
    i = 0
    while True:
        i += 1
        filename = dir + "/p" + str(i) + ".json"
        if not os.path.exists(filename):
            break
        
        try:
            fil = open(filename, 'r')
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
    
        if i == 1:
            #buf = con.read() # read arena
            arena = Arena(buf)
            sched = Scheduler(arena)
            
            #while True:

        else:
            #buf = con.read()
            
            arena.update(buf)
            
        commands = sched.update()
        if not commands is None and len(commands) > 0:
            #con.send(string.join(commands))
            print string.join(commands)
