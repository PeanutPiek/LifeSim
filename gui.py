# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 20:48:47 2021

@author: PeanutFlake
"""

import pygame
from pygame.locals import *

import pygame_gui

from entities import Entity


class GUIComponent():
    def __init__(self, ui_element : pygame_gui.core.ui_element.UIElement):
        self.ui_element = ui_element
        self.on_mouse_click = None
        self.on_key_down = None
    
    def handle_mouse_click(self, event, mouse_pos):
        if self.on_mouse_click is not None and callable(self.on_mouse_click):
            self.on_mouse_click(mouse_pos)
    
    def handle_key_down(self, event, key):
        if self.on_key_down is not None and callable(self.on_key_down):
            self.on_key_down(key)
    
class GUIButtonComponent(GUIComponent):
    def __init__(self, ui_element):
        super().__init__(ui_element)
        self.on_button_click = None
        
    def handle_button_click(self):
        if self.on_button_click is not None and callable(self.on_button_click):
            self.on_button_click(self.ui_element)

class GUIContainer():
    def __init__(self, manager):
        self.manager = manager
        self.container = []
    
    def add(self, component : GUIComponent):
        component.ui_element.manager = self.manager
        self.container.append(component)
        
    def remove(self, component : GUIComponent):
        self.container.remove(component)
        
    def pass_mouse_click_event(self, event, pos):
        for component in self.container:
            component.handle_mouse_click(event, pos)
    
    def pass_key_down_event(self, event):
        for component in self.container:
            component.handle_key_down(event, event.key)
    
    def pass_custom_event(self, event):
        for component in self.container:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if type(component) is GUIButtonComponent \
                    and event.ui_element == component.ui_element:
                    component.handle_button_click()
    
    def process_event(self, event):
        t = event.type
        if t == MOUSEBUTTONUP:
            # Get Mouse Click Position
            pos = pygame.mouse.get_pos()
            # Handle Mouse Click Event
            self.pass_mouse_click_event(event, pos)
        elif t == KEYDOWN:
            # Handle KeyDown Event
            self.pass_key_down_event(event)
        elif t == USEREVENT:
            # Handle Custom Event
            self.pass_custom_event(event)
        # Pass Event to GUIManager
        self.manager.process_events(event)
        
        
class EntityInfoPanel(GUIComponent):
    def __init__(self, world, manager, origin=(5,5)):
        super().__init__(pygame_gui.elements.UIPanel( \
                             relative_rect=pygame.Rect(origin, (200, 300)), \
                             starting_layer_height=1, manager=manager, visible=False))
        self.world = world
        x = self.ui_element.relative_rect.x + origin[0]
        y = self.ui_element.relative_rect.y + origin[1]
        
        y += 25
        self.healthBar = pygame_gui.elements.UIPanel( \
                             relative_rect=pygame.Rect((x, y), (190, 20)), \
                             starting_layer_height=2, parent_element=self.ui_element, manager=manager, visible=False)
        self.healthLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((x, y+15), (190, 20)), \
                                                       text="0", parent_element=self.healthBar, manager=manager, visible=False)
        self.energyBar = pygame_gui.elements.UIPanel( \
                             relative_rect=pygame.Rect((x, y + 15 + 25), (190, 20)), \
                             starting_layer_height=2, parent_element=self.ui_element, manager=manager, visible=False)
        self.energyLabel = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((x, y + 40 + 15), (190, 20)), \
                                                       text="0", parent_element=self.energyBar, manager=manager, visible=False)
        self.taskInfo = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((x, y + 55 + 15), (190, 20)), \
                                                    text="No Task", parent_element=self.ui_element, manager=manager, visible=False)
        self.on_mouse_click = self._mouse_click

    def _mouse_click(self, pos):
        # Offset for clickable Area around an Entity to show InfoPanel
        off = 5
        clicked_entities = [e for e in self.world.entities if e.rect.colliderect(pygame.Rect(pos[0]-off, pos[1]-off, 2*off, 2*off))]
        # If there are Entities clicked
        if len(clicked_entities) > 0:
            # Show Info for first clicked Entity
            # If multiple Entities are in Offset Area of Click, only the first Entity (maybe random) will be displayed.
            self.show(clicked_entities[0])
        else:
            self.hide()
    

    def show(self, entity : Entity):
        
        self.ui_element.visible = True
        
        self.healthBar.visible = True
        self.healthLabel.set_text("{v}".format(v=entity.lifepoints))
        self.healthLabel.rebuild()
        self.healthLabel.visible = True
        
        self.energyBar.visible = True
        self.energyLabel.set_text("{v}".format(v=entity.energy))
        self.energyLabel.rebuild()
        self.energyLabel.visible = True
        
        if entity.current_task is not None:
            tstr = str(type(entity.current_task.strategy))
            tsub = tstr[tstr.index('.')+1:]
            tstr = tsub[:tsub.index("'")]
            self.taskInfo.set_text("{v}".format(v=tstr))
        else:
            self.taskInfo.set_text("No Task")
        self.taskInfo.rebuild();
        self.taskInfo.visible = True
        
        self.energyLabel.visible = True
        
    def hide(self):
        self.ui_element.visible = False
        self.healthLabel.visible = False
        self.healthBar.visible = False
        self.energyLabel.visible = False
        self.energyBar.visible = False
        self.taskInfo.visible = False