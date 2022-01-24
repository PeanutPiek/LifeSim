# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 12:13:24 2021

@author: PeanutFlake
"""

from task import *
from tasks.idle import *
from math_utils import Vector

class FollowMateStrategy(Strategy):
    def __init__(self, max_distance=0, idle_distance=0):
        super().__init__()
        self.target = None
        self.distance = max_distance
        self.idle = idle_distance

    def apply(self, world, task, entity):
        if self.target is None:
            if "Mate" in entity.memory and entity.memory["Mate"] is not None:
                self.target = entity.memory["Mate"]
            else:
                print("Entity knows no Mate")
                task.done = True
        else:
            if not entity.moves():
                entity.step_to(self.target.position())
            else:
                entity.move(world)
                task.done = entity.in_range(self.target, self.distance)
                if task.done:
                    entity.add_task(Task(repeat=False, strategy=IdleMoveStrategy(distance_max=self.idle)))
                    entity.add_task(Task(repeat=False, strategy=FollowMateStrategy(max_distance=self.distance,idle_distance=self.idle)))

class MatingStrategy(Strategy):
    def __init__(self, d_max = 50):
        super().__init__()
        self.target = None
        self.distance_max = d_max
        self.in_range = False
        self.in_mate = 0
        
    def suche_partner(self, world, entity):
        # Für alle Entitäten in der welt
        for e in world.entities:
            # Wenn Entität unterschiedliches Geschlecht
            if e is not entity and \
                (type(entity) is not type(e) and \
                 e.age > 10 and \
                    ("Mate" not in e.memory or \
                        ("Mate" in e.memory and e.memory["Mate"] is None))):
                if entity.position().distance(e.position()) < self.distance_max:
                    # Wähle diese Entität als Ziel
                    return e
        # Keine passende Entität gefuden        
        return None
        
    def apply(self, world, task, entity):
        # Kein Ziel ausgewählt
        if self.target is None:
            print("Suche Ziel für Mating")
            self.target = self.suche_partner(world, entity)
            if self.target is None:
                print("Kein Ziel für Mating gefunden")
                # Beende Task
                task.done = True
                # Führe erneut Mating, von neuer Position aus, aus
                entity.add_task(Task(repeat=False,strategy=MatingStrategy(d_max=self.distance_max)))
                # Führe zuvor IdleMovement aus
                entity.add_task(Task(repeat=False,strategy=IdleMoveStrategy(distance_max=self.distance_max)))
            else:
                print("Found Mate {h}".format(h=hash(self.target)))
        # Ziel wurde bereits gewählt
        else:
            if self.in_mate > 0.0:
                print("In Mate since {s}".format(s=self.in_mate))
                if self.in_mate > 5:
                    world.create_child_entity(entity, self.target)
                    
                    # Aufgabe abgeschloßen
                    task.done = True
                    print("Mating beendet")
                else:
                    self.in_mate += task.delta
            else:
                if "Mate" not in self.target.memory or \
                    ("Mate" in self.target.memory and self.target.memory["Mate"] is None):
                    # Ziel hat noch keinen Mate
                    if entity.in_range(self.target) == True:
                        # Ist in der Nähe des Ziels
                        self.target.memory["Mate"] = entity
                        self.in_mate = .1
                        
                        #self.target.add_task(Task(strategy=FollowMateStrategy(max_distance=5, idle_distance=15), repeat=False))
                        self.target.add_task(Task(strategy=InRangeIdleMoveStrategy(target=entity, max_distance=25, move_idle_min=5, move_idle_max=15), repeat=True))
                    else:
                        # Ist nicht in der Nähe des Ziels
                        # Aktuelle Position
                        o = entity.position()
                        # Aktuelle Position des Ziels
                        p = self.target.position()
                        # Wenn Entität nicht in Bewegung
                        if not entity.moves():
                            # Füge 'Laufstrecke zum Ziel' der Entität hinzu
                            entity.step(Vector(p.x - o.x, p.y - o.y))
                        # Wenn Entität in Bewegung
                        else:
                            # Laufe
                            entity.move(world)
                else:
                    # Ziel hat einen anderen Mate erhalten
                    # Setze Task zurück
                    self.in_mate = 0
                    self.in_range = False
                    self.target = None
