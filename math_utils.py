# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 00:16:36 2021

@author: PeanutFlake
"""

import math

class Vector():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y);
    
    def normalize(self):
        m = self.magnitude()
        if m > 0:
            return Vector(self.x/m, self.y/m)
        return Vector(self.x, self.y)
    
    # Returns the Distance between this Vector and the provided Vector v.
    def distance(self, v):
        return Vector(v.x - self.x, v.y - self.y).magnitude()
    