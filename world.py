# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 01:38:44 2021

@author: PeanutFlake
"""

from pygame.locals import Rect

import constants

import random, sys

from units import *
from tile import *

from hkb_diamondsquare import DiamondSquare as DS

class MapGenerator():
    def __init__(self, tile_size=(1,1)):
        self.tile_size = tile_size
    
    def generate_grid(self, seed, width, height) -> list:
        return []
    
class FlatMapGenerator(MapGenerator):
    def __init__(self, tile_size=(1,1)):
        super().__init__(tile_size=tile_size)
        
    def generate_grid(self, width, height, seed) -> list:
        m = []
        for row in range(height):
            c = []
            for col in range(width):
                c.append(EmptyTile(self.tile_size))
            m.append(c)
        return m
    
class DSMapGenerator(MapGenerator):
    def __init__(self, min_height, max_height, roughness, tile_size=(1,1)):
        super().__init__(tile_size=tile_size)
        self.min_height = min_height
        self.max_height = max_height
        self.roughness = roughness
        
    def generate_grid(self, grid_size_x, grid_size_y, seed=0) -> list:
        tile_grid = []
        
        size = (grid_size_x, grid_size_y)
        mih = self.min_height
        mah = self.max_height
        
        # Generiere 
        heightmap = DS.diamond_square(size, mih, mah, self.roughness, random_seed=seed)
        
        for y in range(0, grid_size_y):
            tile_grid.append([])
            for x in range(0, grid_size_x):
                if heightmap[x][y] < 0:
                    if heightmap[x][y] >= -1:
                        tile_grid[y].append(LowWaterTile(self.tile_size))    
                    else:
                        tile_grid[y].append(WaterTile(self.tile_size))
                elif heightmap[x][y] >= 5:
                    tile_grid[y].append(HillTile(self.tile_size))
                elif heightmap[x][y] >= 8:
                    tile_grid[y].append(MountainTile(self.tile_size))
                else:
                    tile_grid[y].append(GrassTile(self.tile_size))
        return tile_grid
        

class World():
    def __init__(self, size, seed=0, tileSize=(10,10), border=(0,0), background_color=constants.COLOR_WHITE, mapgen=None):
        self.area = Rect((0,0), size)
        self.border = border
        self.entities = []
        self.heights = None
        self.background_color = background_color
        self.tile_size = tileSize
        self.tile_grid = []
        # Initialize World
        self._init_world(seed=seed, generator=mapgen)
        
    def _init_world(self, seed=0, generator=None):
        if seed == 0:
            seed = random.randint(0, sys.maxsize)
        print("Initialize World with Seed={seed}".format(seed=seed))
        
        grid_size_x = int(self.area.size[0]/self.tile_size[0])
        grid_size_y = int(self.area.size[1]/self.tile_size[1])
        
        if generator is not None:
            self.tile_grid = generator.generate_grid(grid_size_x, grid_size_y, seed)                
        
    def update(self, surface, time_delta):
        # Update Entities. Do Entity Logic and redraw.
        for e in self.entities:
            # Update Entity
            e.update(self, time_delta=time_delta)
            # Redraw Entity
            e.draw(surface)
        
    def get_world_size(self):
        return (self.area.width + self.border[0], self.area.height + self.border[1])
    
    # Check if the current Position of the Entity, translated by the given vector is reachable.
    def is_reachable(self, entity, v):
        # If Entity is Ghost
        if entity.ghost:
            # Return Reachable
            return True
        # Predict next Position
        r = entity.rect.move(v.x, v.y)
        # Check Borders
        if r.left < self.area.left or r.top < self.area.top or r.right > self.area.right or r.bottom > self.area.bottom:
            # Return not reachable if outside of World
            return False
        # Check Tile
        tile = self.find_tile(r.center)
        if tile is None or tile.enterable == False:
            # Return not reachable if Tile is not enterable
            return False
        # For all active Entities
        for e in self.entities:
            # If e is not this Entity
            if e is not entity:
                # Check Collision
                if r.colliderect(e.rect):
                    # Return not Reachable if Collision
                    return False
        # Return Reachable
        return True
    
    def find_tile(self, pos):
        if len(self.tile_grid) > 0:
            x = int(pos[0]/self.tile_size[0])
            y = int(pos[1]/self.tile_size[1])
            grid_size_x = int(self.area.size[0]/self.tile_size[0])
            grid_size_y = int(self.area.size[1]/self.tile_size[1])
            #print("Find Tile at {x0};{y0} => {x1};{y1}".format(x0=pos[0],y0=pos[1],x1=x,y1=y))
            if x > 0 and y > 0 and y < grid_size_y and y < grid_size_x:
                return self.tile_grid[y][x]    
        return None
    
    def create_child_entity(self, e1, e2, position=None):
        e = self.create_entity(random.randint(0, 1) == 1, 1)
        if position is None:
            position = ((e1.rect.centerx + e2.rect.centerx) / 2, (e1.rect.centery + e2.rect.centery) / 2)
        e.move_to(position)
    
    def create_random_entity(self, min_age=1, max_age=25):
        e = self.create_entity(random.randint(0, 1) == 1, random.randint(min_age, max_age))
        # Set Position of Entity
        e.move_to(self.get_random_position())
    
    def get_random_position(self):
        # Calculate Position to spawn
        posx = random.randint(self.border[0], self.area.width - self.border[0])
        posy = random.randint(self.border[1], self.area.height - self.border[1])
        position = (posx, posy)
        
        t = self.find_tile(position)
        while t is None or not t.enterable:
            posx = random.randint(self.border[0], self.area.width - self.border[0])
            posy = random.randint(self.border[1], self.area.height - self.border[1])
            print("Generate new Random Position ({x};{y})".format(x=posx,y=posy))
            position = (posx, posy)
            
            t = self.find_tile(position)
        return position
    
    def create_entity(self, male : bool, age):
        e = Male(age) if male == True else Female(age)
        # Add Entity to World
        self.entities.append(e)
        return e
        
    def remove_entity(self, entity):
        if entity is not None:
            if entity in self.entities:
                self.entities.remove(entity)
            del entity
    
    def draw(self, surface):
        cursor = (0,0)
        for row in self.tile_grid:
            for cell in row:
                cell.draw(surface, cursor)
                cursor = (cursor[0] + self.tile_size[0], cursor[1])
            cursor = (0, cursor[1] + self.tile_size[1])
    
    def save(self, file):
        pass