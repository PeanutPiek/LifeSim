# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 02:54:34 2021

@author: PeanutFlake
"""

from task import Strategy

from math_utils import Vector
import random

# Strategie für zufällige Bewegungen.
class IdleMoveStrategy(Strategy):
    def __init__(self, distance_min = 1, distance_max = 1):
        super().__init__()
        self.dist = random.randint(distance_min, distance_max)
        self.target = None
        
    def move_idle(self, world, entity, range=1):
        if not entity.moves():
            v = Vector(random.randint(-1 * range, 1 * range),random.randint(-1 * range, 1 * range))
            entity.step(v)
        return v
        
    def apply(self, world, task, entity):
        if self.target is None:
            self.target = self.move_idle(world, entity, range=self.dist)
        else:
            if entity.moves():
                entity.move(world)
            else:
                self.target = None
                task.done = True

# Strategie für zufällige Bewegungen in Referenz zu einem Ziel.
class InRangeIdleMoveStrategy(IdleMoveStrategy):
    def __init__(self, target=None, max_distance=0, move_idle_min=1, move_idle_max=1):
        super().__init__(distance_min=move_idle_min,distance_max=move_idle_max)
        self.target = target
        self.distance = max_distance

    def apply(self, world, task, entity):
        if self.moves == True:
            super(InRangeIdleMoveStrategy, self).apply(world, task, entity)
        else:
            if not entity.moves():
                if entity.in_range(self.target, self.distance):
                    super(InRangeIdleMoveStrategy, self).apply(world, task, entity)
                else:
                    entity.step_to(self.target.position())
            else:
                entity.move(world)
                task.done = entity.in_range(self.target, self.distance)
