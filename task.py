# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 00:01:32 2021

@author: PeanutFlake
"""

class Strategy():
    def __init__(self):
        pass
    
    def apply(self, world, task, entity):
        pass

class Task():
    def __init__(self, repeat = False, strategy = None):
        self.strategy = strategy
        self.done = False
        self.repeat = repeat
        self.delta = 0
        
    def doTask(self, world, entity, delta):
        self.delta = delta
        # Do Task for Entity by Strategy
        self.strategy.apply(world, self, entity)
        
