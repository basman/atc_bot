#!/usr/bin/python

import unittest
from position import *

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

if __name__ == '__main__':
    unittest.main()
