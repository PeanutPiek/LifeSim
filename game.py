# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 17:24:13 2021

@author: PeanutFlake
"""

import os

import pygame
from pygame.locals import *

import pygame_gui

import gui

from world import World

import constants

import random

class InGameEditor():
    def __init__(self, origin, size, padding=(5,5), manager = None, script_path = "."):
        self.size = size
        self.manager = manager
        
        self.panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(origin, size), starting_layer_height=0, manager=self.manager, visible=False)
        
        self.script_text = ""
        self.script_area = pygame_gui.elements.UITextBox(self.script_text, relative_rect=pygame.Rect((origin[0]+padding[0], origin[1]+padding[1]+100), (size[0]-2*padding[0], size[1] - 2*padding[1] - 150)), manager=self.manager, visible=False, object_id='#script_text')
        self.script_path = script_path
        
        self.dropdown_data = ["Skript auswählen"]
        for file in os.listdir(self.script_path):
            if file.endswith('.py'):
                self.dropdown_data.append(file)
        
        self.dropdown = pygame_gui.elements.UIDropDownMenu(self.dropdown_data, self.dropdown_data[0], relative_rect=pygame.Rect((origin[0]+padding[0], origin[1]+padding[1]), (size[0]-2*padding[0], 40)), manager=self.manager, visible=False, parent_element=self.panel, object_id='#script_chooser')
        
        self.visible = False
        self.focus = None
        
    def on_click(self, pos):
        # Reset focus
        self.focus = None
        if self.script_area.rect.collidepoint(pos):
            self.focus = self.script_area
        elif self.dropdown.rect.collidepoint(pos):
            self.focus = self.dropdown
            
    def update(self, surface):
        if self.visible is True:                
            
            self.dropdown.options_list = self.dropdown_data
            self.reset_dropdown()
            
    def reset_dropdown(self):
        if len(self.dropdown_data) == 0:
            self.dropdown.selected_option = None 
        else: 
            self.dropdown.selected_option = self.dropdown_data[0]
        self.dropdown.rebuild()
        
    def process_mouse_event(self, event, pos):
        if self.visible is True:
            self.on_click(event.pos)
        
    def process_key_event(self, event):
        if self.focus is self.script_area:
            if event.key == K_RETURN:
                self.script_text += "<br>"
            elif event.key == K_BACKSPACE:
                if len(self.script_text) > 0:
                    # New Length of String
                    ind = len(self.script_text)-1
                    # If Current String ends with closing markup
                    if self.script_text[ind] == '>':
                        # Find opening markup
                        ind = self.script_text.rindex('<')
                        # If opening markup is closing Tag
                        if self.script_text[ind+1] == '/':
                            # Find opening Tag
                            ind = self.script_text.rindex('<', end=ind-1)
                    # Cut Text
                    self.script_text = self.script_text[:ind]
            else:
                self.script_text += event.unicode
            self.script_area.html_text = self.script_text
            self.script_area.rebuild()
            self.script_area.set_active_effect('show')
            
    def process_user_event(self, event):
        if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.text.endswith('.py'):
                with open("{path}/{file}".format(path=self.script_path,file=event.text), "r") as f:
                    text = f.read()
                    self.script_text = text.replace("\n", "<br>")
            else:
                self.script_text = ""
            self.script_area.html_text = self.script_text
            self.script_area.rebuild()
        
    def clear_scipt_area(self):
        self.script_area.html_text = ""
        self.script_area.rebuild()
        
    def show(self):
        self.panel.visible = True
        self.script_area.visible = True
        self.dropdown.visible = True
        self.dropdown.show()
        self.visible = True

    def hide(self):
        self.reset_dropdown()
        self.dropdown.selected_option = self.dropdown_data[0]
        self.clear_scipt_area()
        self.focus = None
        self.panel.visible = False
        self.script_area.visible = False
        self.dropdown.visible = False
        self.dropdown.hide()
        self.visible = False

    def toggle(self):
        if self.visible is True: 
            self.hide() 
        else: 
            self.show()

class Game():
    def __init__(self, world : World, tickCount=30, title="LifeSandboxSimulation"):
        self.world = world
        self.tickCount = tickCount
        self.event_listeners = {}
        self.gui_container = None
        self.running = False
        self.manager = None
        self.title = title
        
    def add_event_listener(self, t, f):
        if t not in self.event_listeners:
            self.event_listeners[t] = []
        self.event_listeners[t].append(f)
        
    def remove_event_listener(self, t, f):
        if t in self.event_listeners:
            if f in self.event_listeners[t]:
                self.event_listeners[t].remove(f)
        
    # Initializes PyGame, creates a Window and setup GUI.
    def init(self, theme_file='theme.json'):
        self.FramePerSec = pygame.time.Clock();
        # Init PyGame
        pygame.init()
        # Setup Window
        self.surface = pygame.display.set_mode(self.world.area.size)
        self.surface.fill(constants.COLOR_WHITE)
        # Set Window Title
        pygame.display.set_caption(self.title)
        # Setup UI Manager
        self.manager = pygame_gui.UIManager(self.world.area.size, theme_file)
        self.gui_container = gui.GUIContainer(self.manager)
        # Initialize GUI
        self._init_gui()
    
    # Game-Rendering-Loop
    def run(self):
        self.running = True
        t_delta = 0
        
        while self.running:    
            self._process_events(pygame.event)
            
            self.manager.update(t_delta)

            # Redraw Background
            self.surface.fill(constants.COLOR_WHITE)    
            # Redraw InGameSurface
            self.world.draw(self.surface)
            # Update Game
            self._update(t_delta)
            
            self.manager.draw_ui(self.surface)
            
            pygame.display.flip()
            # Update Clock
            t_delta = self.FramePerSec.tick(self.tickCount)/1000.0
        
    # Exit and cleanup Game
    def dispose(self):
        # Quit
        pygame.quit()
        
    def _init_gui(self):
        
        width = self.world.area.width/2 - self.world.area.width*.1
        editor = InGameEditor((self.world.area.width - width - 5, 5), (width, self.world.area.height - 10), manager=self.manager, script_path='{cwd}/tasks'.format(cwd=os.getcwd()))
        #cEditor = gui.GUIComponent(editor)
        
        button = pygame_gui.elements.UIButton(relative_rect= \
                                              pygame.Rect( \
                                                  (5, self.world.area.height - 55), \
                                                  (50, 50) \
                                              ), text="E", manager=self.manager)
        cButton = gui.GUIButtonComponent(button)
        #cButton.on_button_click = lambda : editor.toggle()
        self.gui_container.add(cButton)
        
        #edetail = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((5, 5), (150, 200)), starting_layer_height=1, manager=self.manager, visible=False)
        #cEdetail = gui.GUIComponent(edetail)
        
        #cEdetail.on_mouse_click = lambda event, pos: 
        
        #self.gui_container.add(cEdetail)
        
        info_panel = gui.EntityInfoPanel(self.world, self.manager)
        self.gui_container.add(info_panel)
        
    # Update Game State with time difference since last call
    def _update(self, td):
        # Update World
        self.world.update(self.surface, time_delta=td)
        
        #self.editor.update(self.surface)
            
    # Handle Game/GUI related Events
    def _process_events(self, events):
        # Check Events
        for event in events.get():
            # Handle Quit Event
            if event.type == QUIT:
                self.running = False;
            else:
                self.gui_container.process_event(event)