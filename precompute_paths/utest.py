#!/usr/bin/python

import unittest
from position import *
from flightpath import FlightPath

class Tests(unittest.TestCase):
    def setUp(self):
        self.posA = Position(1,1,1)
        self.posB = Position(3,1,2)
        self.posC = Position(1,1,2)
        self.posD = Position(2,1,2)

    def testCollision(self):
        self.assertFalse(self.posA.is_collision(self.posB))
        self.assertTrue(self.posA.is_collision(self.posC))
        self.assertTrue(self.posA.is_collision(self.posD))
        self.assertFalse(self.posB.is_collision(self.posC))
        self.assertTrue(self.posB.is_collision(self.posD))
        self.assertTrue(self.posC.is_collision(self.posD))

if __name__ == '__main__':
    unittest.main()
