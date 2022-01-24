# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 23:42:10 2021

@author: PeanutFlake
"""

import math
from math_utils import Vector

import random

import pygame
from pygame.locals import Rect

from queue import Queue

from task import Task
from tasks.idle import IdleMoveStrategy

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
ENTITY_STATE_SOLVE = 1

ENTITY_MAX_STEPS = 1024
ENTITY_MAX_TASKS = 16


class Ability():
    def __init__(self, name, strat_class):
        pass
        self.name = name
        self.strategy_class = strat_class
    
    def invoke(self, entity, obj):
        entity.add_task(Task(repeat=False, strategy=self.strategy_class.__new__()))
        
    def invokable(self, obj):
        pass

class Character:
    def __init__(self):
        self.strength = random.randint(0, 5)
        self.agility = random.randint(0, 5)
        self.inteligence = random.randint(0, 5)
        
        self.abilities = []
        
    def add_ability(self, ability):
        if ability not in self.abilities:
            self.abilities.append(ability)

class Entity(Sprite):
    def __init__(self, color=constants.COLOR_BLACK):
        super().__init__(color, (5, 5))
        # Max Steps to go in a single Movement
        self.max_steps = ENTITY_MAX_STEPS;
        # Init Entity State in Idle
        self.state = ENTITY_STATE_IDLE
        # No Active Task
        self.current_task = None
        # Init Task-Queue as Fifo
        self.task_queue = Queue(ENTITY_MAX_TASKS)
        # Init Move-Queue as Fifo
        self.move_queue = Queue(self.max_steps)
        # Is Ghost
        self.ghost = False
        # Health of Entity
        self.lifepoints = 100
        # Stamina/Energy of Entity
        self.energy = 100
        # "Character-Sheet" of this Entity, which hold Attributes and Abilities
        self.character = Character()
        # DataMap to save Key:Value Pairs, epecific for this Entity, for reusability
        self.memory = {}
        
    # Initializes a Cell in the Memory of this Entity
    def _init_mem(self, key, value=None):
        self.memory[key] = value
        
    # Put an Key:Value Pair into Memory of this Entity
    def put_mem(self, key, value, ttl=0):
        if key not in self.memory:
            self._init_mem(key, value)
        else:
            self.memory[key] = value
        
    # Adds a absolute Position as Target to move to for this Entity.    
    def step_to(self, v) -> bool:
        p = self.position()
        x = v.x - p.x
        y = v.y - p.y
        return self.step(Vector(x,y))
        
    # Adds a relative Offset (Translation) to step. 
    # The Translation will be added as Steps to Move Queue. Every Step is of length 1.
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
        #print("Current Steps = {steps}".format(steps = self.move_queue.qsize()))
        # If required Steps is lower or equals the max available Steps
        if m <= self.max_steps:
            #print("Move Entity({c}) from ({from_x};{from_y}) to ({to_x};{to_y}), Steps={steps}, Magnitude={mag}".format(c=type(self), from_x=self.rect.centerx, from_y=self.rect.centery, to_x=self.rect.centerx+v.x, to_y=self.rect.centery+v.y, steps=steps, mag=m))
            # Add sequential Steps to Move Queue
            for n in range(steps):
                # Direction from current Location to Target
                vd = Vector(px-ox, py-oy).normalize()
                # Calculate Step Target Position
                vpx = math.ceil(vd.x) if vd.x > 0 else math.floor(vd.x)
                vpy = math.ceil(vd.y) if vd.y > 0 else math.floor(vd.y)
                vp = Vector(vpx, vpy)
                # Add Step Target to Move Queue
                self.move_queue.put(vp, timeout=100)
                # Add Translate to current Location
                ox = ox + vp.x
                oy = oy + vp.y
            #print("Added {num} Steps to Entity".format(num=steps))
            return True
        else:
            # The Translation require more Steps as possible, ignore Move Request.
            print("Path too long!")
            return False
            
    # Move Entity by next Translation from Move Queue if reachable, else reset Move-Queue. 
    # If there is no Translation in Queue, do nothing.
    def move(self, world):
        try:
            # Get Item from Queue without blocking
            v = self.move_queue.get(False)
            # If there is a Translation
            if v is not None:
                # If the Target Point is reachable
                if world.is_reachable(self, v):
                    # Define Base Energy required to Move
                    energyRequired = 0.5
                    # Find Tile Entity moves on
                    p = self.position()
                    tile = world.find_tile((p.x, p.y))
                    if tile is not None:
                        energyRequired *= tile.energyRequiredMultiplier
                        
                    # If Entity has enough Energy
                    if self.energy >= energyRequired:
                        # Move Entity
                        self.rect.move_ip(v.x, v.y)
                        # Substract EnergyRequired
                        self.energy -= energyRequired
                    else:
                        print("Out of Energy to Move")
                else:
                    # Obstacle detected
                    print("Obstacle!")
                    # Reset Move-Queue
                    self.move_queue.queue.clear()
        except:
            # Ignore Empty Exception from Queue
            pass
    
    def update(self, world, time_delta):
        if self.lifepoints <= 0:
            world.remove_entity(self)
            return
        
        # If Energy is not full
        if self.energy < 100.0:
            # Restore a bit of Energy
            self.energy += .2

        # If Entity has no current Task
        if self.current_task is None:
            # Try next Task in Queue as new active Task
            if not self.task_queue.empty():
                self.current_task = self.task_queue.get(False)
        # If there is a Task to proceed
        if self.current_task is not None:
            # Do next solving step
            self.solve(world, self.current_task, time_delta=time_delta)
        else:
            if self.energy < 100.0:
                # Entity is idle, restore an additional bit of Energy
                self.energy += .1
            self.think(time_delta)
    
    def task_complete(self):
        pass
    
    def in_range(self, other, max_distance=0):
        if self is other:
            return True
        md = math.sqrt(pow(self.rect.size[0],2)+pow(self.rect.size[1],2)) + max_distance
        return Vector(self.rect.centerx, self.rect.centery).distance(Vector(other.rect.centerx, other.rect.centery)) < md
    
    # Returns the current Position of this Entity as Vector
    def position(self) -> Vector:
        return Vector(self.rect.centerx, self.rect.centery)
        
    # Returns if this Entity is currently moving
    def moves(self) -> bool:
        return not self.move_queue.empty()
        
    # Returns the next Task from Task Queue
    def find_next_task(self) -> Task:
        if not self.task_queue.empty():
            return self.task_queue.get(False)
        return None
    
    # Add a new Task to Task Queue
    def add_task(self, task):
        print("Current Size of Queue: {s}, add new Task {t} to Entity {e}".format(s=self.task_queue.qsize(),t=type(task.strategy), e =hash(self)))
        if not self.task_queue.full():
            self.task_queue.put_nowait(task)
        
    def think(self, time_delta):
        #print("think")
        # If Entity has enough Energy and no Task is waiting
        if self.energy >= 100 and self.task_queue.empty():
            # Add a new IdleTask
            # "Stupidity-Factor" or "Int" to trigger Idle Tasks random
            self.add_task(Task(strategy=IdleMoveStrategy(distance_max=50)))
        
    # Solve Task. If no Task is provided, solve active Task. 
    # If there is no active Task too, add a new IdleTask if Entity is in Idle State.
    def solve(self, world, task=None, time_delta=0):
        # If Task is provided
        if task is not None:
            # Override current Task
            self.current_task = task
        # If there is an active Task
        if self.current_task is not None:
            # Set current State to Solving
            self.state = ENTITY_STATE_SOLVE
            # If active Task has Solving-Strategy
            if self.current_task.strategy is not None:
                # Do Task for Entity
                self.current_task.doTask(world, self, time_delta)
                # If Task is done
                if self.current_task.done:
                    self.task_complete()
                    # If Task should be repeated
                    if self.current_task.repeat == True:
                        # Add Copy of Task to End of Queue
                        self.current_task.done = False
                        self.add_task(self.current_task)
                    # Clear active Task
                    self.current_task = None
                    # Current Task acomplished, set to Idle State until next Task
                    self.state = ENTITY_STATE_IDLE
            # If active Task has no Solving-Strategy
            else:
                # Inform User
                print("Task has no Strategy for solving")
        # If there is no active Task
        else:
            self.think(time_delta)