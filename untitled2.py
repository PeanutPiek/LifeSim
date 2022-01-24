# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 21:22:41 2021

@author: PeanutFlake
"""

from pygame import Rect, Color

class TextInputBox():
    def __init__(self, x, y, w, h):
        self.rect = Rect((x,y), (w,h))
        self.color = Color("#25292e")