# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 01:38:44 2021

@author: PeanutFlake
"""

import pygame
from pygame.locals import Rect

import numpy as np;
import random;

import constants
import png

class World():
    def __init__(self, size, origin=(0,0), background_color=constants.COLOR_WHITE):
        self.borders = Rect(origin, size)
        self.entities = []
        self.heights = None
        self.background_color = background_color
        
    def add_entity(self, entity):
        self.entities.append(entity)
        
    def generate(self):
        s = (self.borders.width, self.borders.height)
        a = np.zeros(s, dtype=float)
        print("Generate Map of Size " + s)
        
        a[0,0] = np.random.ranf()
        a[0,np.size(a,1)-1] = np.random.ranf()
        a[np.size(a,0)-1,0] = np.random.ranf()
        a[np.size(a,0)-1,np.size(a,1)-1] = np.random.ranf()
        
        self.heights = self.generate_chunk(a, s)
        
        win = pygame.display.set_mode(s)
        pygame.display.set_caption("World Background")
        
        win.fill(constants.COLOR_WHITE)
        
        for y in range(s[1]):
            row = ()
            for x in range(s[0]):
                win.set_at((x,y), self.get_color_at(x, y))
        
        pygame.image.save(win, "world_background.png")
        
    
    def generate_chunk(self, ma, sh, offset_x = 0, offset_y = 0, offset_height = 0):
        
        su = (ma[0 + offset_x,0 + offset_y] + ma[0 + offset_x,sh[1]-1+offset_y] + ma[sh[0]-1+offset_x, 0 + offset_y] + ma[sh[0]-1+offset_x, sh[1]-1+offset_y])/4
        ma[int(sh[0]/2)-1+offset_x,int(sh[1]/2)-1+offset_y] = min(max(su + (np.random.ranf()-0.5)/10, 0.0), 1.0) + offset_height
        
        if ma[int(sh[0]/2)-1+offset_x,0 + offset_y] == 0:
            sm0 = (ma[0 + offset_x,0 + offset_y] + ma[0 + offset_x,sh[1]-1+offset_y] + ma[int(sh[0]/2)-1+offset_x,int(sh[1]/2)-1+offset_y]) / 3
            ma[int(sh[0]/2)-1,0 + offset_y] = min(max(sm0 + (np.random.ranf()-0.5)/10, 0.0), 1.0) + offset_height

        if ma[sh[0]-1+offset_x, int(sh[1]/2)-1+offset_y] == 0:
            sm1 = (ma[0 + offset_x,sh[1]-1+offset_y] + ma[sh[0]-1+offset_x,sh[1]-1+offset_y] + ma[int(sh[0]/2)-1+offset_x,int(sh[1]/2)-1+offset_y]) / 3
            ma[sh[0]-1+offset_x, int(sh[1]/2)-1+offset_y] = min(max(sm1 + (np.random.ranf()-0.5)/10, 0.0), 1.0) + offset_height

        if ma[int(sh[0]/2)-1+offset_x, sh[1]-1+offset_y] == 0:
            sm2 = (ma[0 + offset_x, sh[1]-1+offset_y] + ma[sh[0]-1+offset_x,sh[1]-1+offset_y] + ma[int(sh[0]/2)-1+offset_x,int(sh[1]/2)-1+offset_y]) / 3
            ma[int(sh[0]/2)-1+offset_x, sh[1]-1+offset_y] = min(max(sm2 + (np.random.ranf()-0.5)/10, 0.0), 1.0) + offset_height

        if ma[0 + offset_x, int(sh[1]/2)-1+offset_y] == 0:         
            sm3 = (ma[0 + offset_x, 0 + offset_y] + ma[sh[0]-1+offset_x, 0 + offset_y] + ma[int(sh[0]/2)-1+offset_x,int(sh[1]/2)-1+offset_y]) / 3
            ma[0 + offset_x, int(sh[1]/2)-1+offset_y] = min(max(sm3 + (np.random.ranf()-0.5)/10, 0.0), 1.0) + offset_height
        
        sha = (int(sh[0]/2), int(sh[1]/2))
        if sha[0] >= 3 and sha[1] >= 3:
            ma = self.generate_chunk(ma, sha, offset_height=offset_height)
            ma = self.generate_chunk(ma, sha, offset_x=sha[0], offset_height=offset_height)
            ma = self.generate_chunk(ma, sha, offset_y=sha[1], offset_height=offset_height)
            ma = self.generate_chunk(ma, sha, offset_x=sha[0], offset_y=sha[1], offset_height=offset_height)
        
        return ma
    
    def get_color_at(self, x, y):
        color = self.background_color
        if self.heights is not None:
            h = self.heights[x,y]
            if h > .9:
                color = constants.COLOR_WHITE
            elif h > .7:
                color = constants.COLOR_GREY_LIGHT
            elif h > .3:
                color = constants.COLOR_GREEN_LIGHT
            elif h > .2:
                color = constants.COLOR_BLUE_LIGHT
            elif h > .01:
                color = constants.COLOR_BLUE
            else:
                color = constants.COLOR_BLACK
        return color
        
    
    def draw(self, surface, screen):
        for x in range(screen[0]):
            for y in range(screen[1]):
                surface.set_at((x,y), self.get_color_at(x,y))