# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 00:07:35 2021

@author: PeanutFlake
"""

from entities import Entity, ENTITY_GENDER_FEMALE, ENTITY_GENDER_MALE

from constants import *
from tasks import MatingTask

class Child(Entity):
    def __init__(self, world, gender):
        super().__init__(world, gender)
        
class Senior(Entity):
    def __init__(self, world, gender):
        super().__init__(world, gender)
            
class Adult(Entity):
    def __init__(self, world, gender):
        super().__init__(world, gender)
        
class Male(Adult):
    def __init__(self, world):
        super().__init__(world, ENTITY_GENDER_MALE)
        self.color = COLOR_BLUE
        
class Female(Adult):
    def __init__(self, world):
        super().__init__(world, ENTITY_GENDER_FEMALE)
        self.color = COLOR_RED
        self.add_task(MatingTask(self))