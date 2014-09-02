#!/usr/bin/python

import unittest
from position import Position
import scheduler
import arena
import connector
import string

class Tests(unittest.TestCase):
    def setUp(self):
        self.posA = Position(1,1,1,0)
        self.posB = Position(3,1,2,0)
        self.posC = Position(1,1,2,0)
        self.posD = Position(2,1,2,0)

        self.posA1 = Position(1,1,1,0,90)
        self.posB1 = Position(1,1,1,315,90)
        self.posC1 = Position(1,1,1,45,90)
        self.posD1 = Position(1,1,1,135,90)
        self.posE1 = Position(1,1,1,225,90)
        self.posF1 = Position(1,1,1,270,90)


    def testCollision(self):
        self.assertFalse(self.posA.is_collision(self.posB))
        self.assertTrue(self.posA.is_collision(self.posC))
        self.assertTrue(self.posA.is_collision(self.posD))
        self.assertFalse(self.posB.is_collision(self.posC))
        self.assertTrue(self.posB.is_collision(self.posD))
        self.assertTrue(self.posC.is_collision(self.posD))

    def testDirection(self):
        self.assertTrue(self.posA1.equals(self.posB1))
        self.assertTrue(self.posA1.equals(self.posC1))
        self.assertFalse(self.posA1.equals(self.posD1))
        self.assertFalse(self.posA1.equals(self.posE1))
        self.assertTrue(self.posA1.equals(self.posF1))
        
        self.assertTrue(self.posB1.equals(self.posC1))
        self.assertFalse(self.posB1.equals(self.posD1))
        self.assertTrue(self.posB1.equals(self.posE1))
        self.assertTrue(self.posB1.equals(self.posF1))
        
        self.assertTrue(self.posC1.equals(self.posD1))
        self.assertFalse(self.posC1.equals(self.posE1))
        self.assertFalse(self.posC1.equals(self.posF1))

        self.assertTrue(self.posD1.equals(self.posE1))
        self.assertFalse(self.posD1.equals(self.posF1))

        self.assertTrue(self.posE1.equals(self.posF1))

        # not the same, the other way round
        self.assertTrue(self.posB1.equals(self.posA1))
        self.assertTrue(self.posC1.equals(self.posA1))
        self.assertFalse(self.posD1.equals(self.posA1))
        self.assertFalse(self.posE1.equals(self.posA1))
        self.assertTrue(self.posF1.equals(self.posA1))
        
        self.assertTrue(self.posC1.equals(self.posB1))
        self.assertFalse(self.posD1.equals(self.posB1))
        self.assertTrue(self.posE1.equals(self.posB1))
        self.assertTrue(self.posF1.equals(self.posB1))
        
        self.assertTrue(self.posD1.equals(self.posC1))
        self.assertFalse(self.posE1.equals(self.posC1))
        self.assertFalse(self.posF1.equals(self.posC1))

        self.assertTrue(self.posE1.equals(self.posD1))
        self.assertFalse(self.posF1.equals(self.posD1))

        self.assertTrue(self.posF1.equals(self.posE1))

    def testAscentImmediateDescent(self):
        arena_data = '{ "width": 30, "height": 21, "update": 1, "newplane": 4, "clock": 1, ' + \
                      '"exits": [ ' + \
                      '          { "id": 0, "x": 29, "y": 7, "dir": 270 }' + \
                      '          ],  ' + \
                      '"airports": [ { "id": 0, "x": 20, "y": 18, "dir": 90 } ],  ' + \
                      '"beacons": [],  ' + \
                      '"lines": [],  ' + \
                      '"airplanes": [ ' + \
                      '               { "id": "a", "x": 5, "y": 5, "alt": 7, "dir": 90, "fuel": 30, "dest": "E0" }, ' + \
                      '               { "id": "C", "x": 5, "y": 5, "alt": 7, "dir": 90, "fuel": 30, "dest": "E0" } ' + \
                      '              ] ' + \
                      '}'

        ar = arena.Arena(arena_data)
        sched = scheduler.Scheduler(ar, connector.DummyConnector())
        
        path = [
                Position(19,16,1, 90),
                Position(19,17,2,180),
                Position(19,18,1,180),
                Position(20,18,0,90)
                ]
        t = 1
        for p in path:
            p.time = t
            t += 1
            
        sched._compute_commands(path, ar.airplanes['a'])
        print "path: " + string.join(map(str, path), ', ')
        
        self.assertTrue('a2' in path[0].cmd)
        self.assertTrue('a0' in path[1].cmd)
        
        path2 = [
                Position(10,16,1,90),
                Position(11,16,1,90),
                Position(12,16,1,90),
                Position(13,16,1,90),
                Position(13,17,2,180),
                Position(13,17,2,180),
                Position(13,18,1,180),
                Position(13,18,1,180),
                Position(14,18,0,90)
                ]
        t = 1
        for p in path2:
            p.time = t
            t += 1
        
        sched._compute_commands(path2, ar.airplanes['C'])
        print "path2: " + string.join(map(str, path2), ', ')

        self.assertTrue('a2' in path2[3].cmd)
        self.assertTrue('a0' in path2[5].cmd)


if __name__ == '__main__':
    unittest.main()
