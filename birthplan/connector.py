import socket
import re
import time

class DummyConnector:
    # eats commands
    def send(self, s):
        print "emitted commands: " + ','.join(s.split())

class Connector:
    def __init__(self, server='localhost', port=2028):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msg_queue = []
        print "connecting",
        for i in range(2000):
            try:
                self.s.connect((server, port))
                print "success"
                break
            except IOError as err:
                print '.',
                time.sleep(0.2)
        else:
            print ""
            raise IOError("connection failed")
    
    
    def send(self, msg):
        self.s.send(msg)
        
    def read(self, bufsize=1024*16):
        if len(self.msg_queue) == 0:
            try:
                buf = self.s.recv(bufsize)
                if len(buf) == 0:
                    print "Client disconnected (len=0)"
                    exit(0)
                messages = re.split("\n}\n", buf)
                for msg in messages:
                    if len(msg) > 0:
                        self.msg_queue.append(msg + "\n}\n")
            except IOError as err:
                print "Client disconnected"
                exit(1)
        m = self.msg_queue.pop(0)
        #print "received: '" + m + "'"
        return m