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

    def executer(self):
        super().executer()
        self.jeu.executer_action(random.choice(self.actions_possibles))
        self.complete = True
