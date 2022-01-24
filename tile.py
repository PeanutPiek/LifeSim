# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 14:28:10 2021

@author: PeanutFlake
"""

import pygame

from pygame.rect import Rect


class Tile():
    def __init__(self, size, color):
        self.rect = Rect((0,0),size)
        self.color = color
        self.enterable = True
        
        self.energyRequiredMultiplier = 1
    
    def draw(self, surface, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        pygame.draw.rect(surface, self.color, self.rect)
        
class EmptyTile(Tile):
    def __init__(self, size):
        super().__init__(size, (255, 255, 255))
        
class HillTile(Tile):
    def __init__(self, size):
        super().__init__(size, (102, 102, 0))
        
        self.energyRequiredMultiplier = 1.25
        
class MountainTile(Tile):
    def __init__(self, size):
        super().__init__(size, (128, 128, 128))
        
        self.energyRequiredMultiplier = 2
        
class GrassTile(Tile):
    def __init__(self, size):
        super().__init__(size, (0, 100, 0))
        
        self.energyRequiredMultiplier = 0.75
        
class WaterTile(Tile):
    def __init__(self, size):
        super().__init__(size, (0, 0, 128))
        self.enterable = False
        
        self.energyRequiredMultiplier = 1.75
        
class LowWaterTile(Tile):
    def __init__(self, size):
        super().__init__(size, (0, 0, 255))
        self.enterable = False
        
        self.energyRequiredMultiplier = 1.5