import pygame
from .Action import Action
import random
class RandomAction(Action):
    """
    Action qui exécute une action aléatoire parmi une liste d'actions possibles.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.actions_possibles = data.get("actions_possibles", [])
        self.action_choisie = None

    def update(self, events):
        if self.action_choisie is None:
            action_data = random.choice(self.actions_possibles)
            action_type = action_data.get("type")
            action_class = self.jeu.get_action_class_by_type(action_type)
            if action_class:
                self.action_choisie = action_class(self.jeu, action_data)
                self.action_choisie.executer()
        else:
            if self.action_choisie.complete:
                self.complete = True
            else:
                self.action_choisie.update(events)

    def draw(self):
        if self.action_choisie:
            self.action_choisie.draw()