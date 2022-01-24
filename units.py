# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 00:07:35 2021

@author: PeanutFlake
"""

from entities import Entity, Ability

from constants import COLOR_BLUE, COLOR_RED
from task import Task
from tasks.mate import MatingStrategy
from tasks.idle import IdleMoveStrategy

class Subject(Entity):
    def __init__(self, age):
        super().__init__()
        self.age = age
        
    def size(self):
        s=min(self.age, 3)
        return [s,s]
    
    def update(self, world, time_delta):
        self.age += time_delta/60
        super(Subject, self).update(world, time_delta)
        
    def draw(self, surface):
        self.rect.size = self.size()
        super(Subject, self).draw(surface)
        
class Male(Subject):
    def __init__(self, age):
        super().__init__(age=age)
        self.color = (0, 0, 200)
        
class Female(Subject):
    def __init__(self,age):
        super().__init__(age=age)
        self.color = (200, 0, 0)
        
        self.memory["Mate"] = None
        self.last_mate = 0
            
        self.character.add_ability(Ability("Paarung", type(MatingStrategy)))
        
    def think(self, time_delta):
        if self.memory["Mate"] is None:
            if self.age > 10:
                if self.last_mate > 2:
                    self.add_task(Task(repeat=False, strategy=MatingStrategy()))
                    self.last_mate = 0
                else:
                    self.last_mate += time_delta
                    self.add_task(Task(repeat=False, strategy=IdleMoveStrategy(distance_max=50)))
                    print("Last Mate at {n}".format(n=self.last_mate))