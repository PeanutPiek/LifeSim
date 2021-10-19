# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 00:01:32 2021

@author: PeanutFlake
"""

import random
from math_utils import Vector

class Strategy():
    def __init__(self):
        pass
    
    def handle(self, task, entity):
        pass

class Task():
    def __init__(self, repeat = False):
        self.target = None
        self.strategy = None
        self.done = False
        self.repeat = repeat
        
    def doit(self, entity):
        # Do Task for Entity by Strategy
        self.strategy.handle(self, entity)

class MatingStrategy(Strategy):
    def __init__(self, d_max = 50):
        super().__init__()
        self.target = None
        self.distance_max = d_max
        
    def handle(self, task, entity):
        if self.target is None:
            for e in entity.world.entities:
                if e is not entity and self.is_diff_gender(entity, e):
                    o = entity.position()
                    p = e.position()
                    d = o.distance(p)
                    if d < self.distance_max:
                        self.target = e
                        break
        else:
            if not entity.moves():
                o = entity.position()
                p = self.target.position()
                entity.step(Vector(p.x - o.x, p.y - o.y))
                
        entity.move()
        if not entity.moves():
            task.done = True
            
    def is_diff_gender(self, e1, e2) -> bool:
        return e1.gender != e2.gender
            

class MatingTask(Task):
    def __init__(self, repeat=True):
        super().__init__(repeat)
        self.strategy = MatingStrategy()
        
class IdleMoveStrategy(Strategy):
    def __init__(self, distance = 1):
        super().__init__()
        self.dist = distance
        
    def move_idle(self, entity, range=1):
        if not entity.moves():
            v = Vector(random.randint(-1 * range, 1 * range),random.randint(-1 * range, 1 * range))
            entity.step(v)
        entity.move()
        
    def handle(self, task, entity):
        self.move_idle(entity, self.dist)
        if not entity.moves():
            task.done = True
        
class IdleTask(Task):
    def __init__(self):
        super().__init__(False)
        self.strategy = IdleMoveStrategy(random.randint(1, 50))