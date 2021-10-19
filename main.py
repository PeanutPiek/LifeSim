# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pygame
from pygame.locals import QUIT

import sys, random

from constants import COLOR_WHITE
from units import Male, Female

from world import World

# Window Size
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 100

# Frames per Second
FPS = 30

# Initial Count of Entities
COUNT_OF_ENTITIES = 10



# Initialize List of Entities
def init_entities(world, n, border = 10):
    for i in range(n):
        e = None
        # 50:50 distribution of Genders
        if random.randint(0, 1) == 1:
            e = Male(world)
        else:
            e = Female(world)
        # Calculate Position to spawn
        pos = (random.randint(border, SCREEN_WIDTH - border), random.randint(border, SCREEN_HEIGHT - border))
        # Set Position of Entity
        e.move_to(pos)
        # Add Entity to World
        world.add_entity(e)   

# Update Entities. Do Entity Logic and redraw.
def update_entities(entities, surface):
    for e in entities:
        task = e.get_current_task()
        if task is None:
            # If no active Task is handeled
            # Try pass next Task in Queue as new active Task
            task = e.find_next_task()
            e.solve(task)
        else:
            # If active Task is handeled
            # Do next solving step
            e.solve()
            
        e.draw(surface)

FramePerSec = pygame.time.Clock();

pygame.init()
# Setup Window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT));
DISPLAYSURF.fill(COLOR_WHITE)
# Set Window Title
pygame.display.set_caption("LifeSim")

# Setup World
w = World((SCREEN_WIDTH, SCREEN_HEIGHT))
w.generate()
# List of Entities in Game
init_entities(w, COUNT_OF_ENTITIES)

# Main Loop
active = True
while active:    
    # Check Events
    for event in pygame.event.get():
        if event.type == QUIT:
            active = False;
    # Update Display
    pygame.display.update()
    # Redraw Background
    DISPLAYSURF.fill(COLOR_WHITE)        
    #w.draw(DISPLAYSURF, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Update Entities of World
    update_entities(w.entities, DISPLAYSURF)
    # Update Clock
    FramePerSec.tick(FPS)
    
# Quit
pygame.quit()
sys.exit()