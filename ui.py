# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 21:22:41 2021

@author: PeanutFlake
"""

from pygame import Rect, Color, font, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, draw

class TextInputBox():
    def __init__(self, x, y, w, h):
        self.rect = Rect((x,y), (w,h))
        self.color = Color("#25292e")
        self.color_text = Color("#ffffff")
        self.text = ""
        self.font = font.Font(None, 32)
        self.surface = self.render()
        self.cursor_pos = None
        
    def render(self):
        return self.font.render(self.text, True, self.color_text)
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.cursor_pos = 0        
            else:
                self.cursor_pos = None
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text = self.text + event.unicode
            self.surface = self.render()
            
    def update(self):
        pass
    
    def draw(self, surface):
        surface.blit(self.surface, (self.rect.x+5, self.rect.y+5))
        draw.rect(surface, self.color, self.rect, 2)