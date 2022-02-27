# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from game import Game
from world import *
import sys

#################################
#                               #
# Define Initial Parameters.    #
#                               #
#################################

# Frames per Second to calculate, depends on system performance and results in game speed
FPS = 30

# Window Size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initial Count of Entities, Entities will supposed to be generated ~50/50 as Male/Female
COUNT_OF_ENTITIES = 100
# Size of Tiles in generated Map
TILESIZE = (10,10)
# Define Map Generator
# Empty/Flat World
#gen = FlatMapGenerator(tile_size=TILESIZE)
# Generated World on Heightmap
gen = DSMapGenerator(min_height=-5, max_height=10, roughness=0.25, tile_size=TILESIZE)

# Create World
world = World(size=(SCREEN_WIDTH,SCREEN_HEIGHT), border=(10,10), tileSize=TILESIZE, mapgen=gen)

# Create Game Instance
game = Game(world=world, tickCount=FPS)

print("Initialize Game.")
game.init()
# Game is initialized, lets spawn some Entities
for i in range(COUNT_OF_ENTITIES):
    world.create_random_entity(min_age=15)

print("Start Game.")
game.run()
# Game blocks while running, next Line will be called after Game stops running
print("Terminate Game.")
# Clear Game
game.dispose()
print("Game is closed, bye.")
# Exit Program
sys.exit()

