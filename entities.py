# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 23:42:10 2021

@author: PeanutFlake
"""

import math
from math_utils import Vector

import pygame
from pygame.locals import Rect

from queue import LifoQueue

from tasks import Task, IdleTask

import constants


# Graphical Base Element of Everything in World.
class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, size):
        super().__init__()
        self.color = color
        self.rect = Rect((0, 0), size)

    def move_to(self, pos):
        self.rect.center = pos

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        

ENTITY_STATE_IDLE = 0

ENTITY_GENDER_MALE = "M"
ENTITY_GENDER_FEMALE = "F"

ENTITY_MAX_STEPS = 256
ENTITY_MAX_TASKS = 16


class Entity(Sprite):
    def __init__(self, world, gender, color=constants.COLOR_BLACK):
        super().__init__(color, (5, 5))
        # World in which the Entity lives
        self.world = world
        # Max Steps to go in a single Movement
        self.max_steps = ENTITY_MAX_STEPS;
        # Init Entity State in Idle
        self.state = ENTITY_STATE_IDLE
        # No Active Task
        self.task = None
        # Init Task-Queue as Lifo (Stack)
        self.task_queue = LifoQueue(ENTITY_MAX_TASKS)
        # Init Move-Queue as Lifo (Stack)
        self.move_queue = LifoQueue(self.max_steps)
        # Is Ghost
        self.ghost = False
        # Gender
        self.gender = gender
        # Start with 100 Lifepoints
        self.lifepoints = 100
        
    # Check if the current Position, translated by the given vector is reachable by this Entity.
    def is_reachable(self, v):
        # If Entity is Ghost
        if self.ghost:
            # Return Reachable
            return True
        # Predict next Position
        r = self.rect.move(v.x, v.y)
        # Check Borders
        if r.left < self.world.borders.left or r.top < self.world.borders.top or r.right > self.world.borders.right or r.bottom > self.world.borders.bottom:
            # Return not reachable if outside of World
            return False
        # For all active Entities
        for e in self.world.entities:
            # If e is not this Entity
            if e is not self:
                # Check Collision
                if r.colliderect(e.rect):
                    # Return not Reachable if Collision
                    return False
        # Return Reachable
        return True
        
    # Adds a relative Offset (Translation) to step. 
    # The Translation will be added as Steps to Move Queue. Every Step is of max Length 1.
    # The count of required steps is equal to the magnitude of the Offset.
    # Only Translations as near as 'max_steps' are computed. 
    # If a Translation is too far away there is no Path generated and the Translation will be ignored.
    def step(self, v) -> bool:
        # Length of Translation
        m = v.magnitude()
        # Direction of Translation
        vn = v.normalize()
        # Required Steps to move to target
        steps = math.ceil(m)
        # Current Location
        ox = self.rect.centerx
        oy = self.rect.centery
        # Target Location
        px = ox+v.x
        py = oy+v.y
        # If required Steps is lower or equals the max available Steps
        if m <= self.max_steps:
            print("Move Entity({c}) from ({from_x};{from_y}) to ({to_x};{to_y}), Steps={steps}, Magnitude={mag}".format(c=type(self), from_x=self.rect.centerx, from_y=self.rect.centery, to_x=self.rect.centerx+v.x, to_y=self.rect.centery+v.y, steps=steps, mag=m))
            print("Current Steps= {steps}".format(steps = self.move_queue.qsize()))
            # Add sequential Steps to Move Queue
            for n in range(steps):
                # Direction from current Location to Target
                vd = Vector(px-ox, py-oy).normalize()
                # Calculate Step Target Position
                vpx = math.ceil(vd.x) if vd.x > 0 else math.floor(vd.x)
                vpy = math.ceil(vd.y) if vd.y > 0 else math.floor(vd.y)
                vp = Vector(vpx, vpy)
                # Add Step Target to Move Queue
                self.move_queue.put_nowait(vp)
                # Add Translate to current Location
                ox = ox + vp.x
                oy = oy + vp.y
            return True
        else:
            # The Translation require more Steps as possible, ignore Move Request.
            print("Path too long!")
            return False
            
    # Move Entity by next Translation from Move Queue if reachable, else reset Move-Queue. 
    # If there is no Translation in Queue, do nothing.
    def move(self):
        try:
            # Get Item from Queue without blocking
            v = self.move_queue.get(False)
            # If there is a Translation
            if v is not None:
                # If the Target Point is reachable
                if self.is_reachable(v):
                    # Move Entity
                    self.rect.move_ip(v.x, v.y)
                else:
                    # Obstacle detected
                    print("Obstacle!")
                    # Reset Move-Queue
                    self.move_queue = LifoQueue(self.max_steps)
        except:
            # Ignore Empty Exception from Queue
            pass
    
    # Returns the current Position of this Entity as Vector
    def position(self) -> Vector:
        return Vector(self.rect.centerx, self.rect.centery)
        
    # Returns if this Entity is currently moving
    def moves(self) -> bool:
        return not self.move_queue.empty()
        
    # Returns the next Task from Task Queue
    def find_next_task(self) -> Task:
        if not self.task_queue.empty():
            return self.task_queue.get()
        return None
    
    # Returns the active Task
    def get_current_task(self) -> Task:
        return self.task
    
    # Add a new Task to Task Queue
    def add_task(self, task):
        self.task_queue.put_nowait(task)
        
    # Solve Task. If no Task is provided, solve active Task. 
    # If there is no active Task too, add a new IdleTask if Entity is in Idle State.
    def solve(self, task=None):
        # If Task is provided
        if task is not None:
            # Override current Task
            self.task = task
        # If there is an active Task
        if self.task is not None:
            # If active Task has Solving-Strategy
            if self.task.strategy is not None:
                # Do Task for Entity
                self.task.doit(self)
                # If Task is done
                if self.task.done:
                    # If Task should be repeated
                    if self.task.repeat:
                        # Add Copy of Task to End of Queue
                        self.task.done = False
                        self.add_task(self.task)
                    # Clear active Task
                    self.task = None
            # If active Task has no Solving-Strategy
            else:
                # Inform User
                print("Task has no Strategy for solving")
        # If there is no active Task
        else:
            # If Entity is in Idle State
            if self.state is ENTITY_STATE_IDLE:
                # Add a new IdleTask
                self.add_task(IdleTask())