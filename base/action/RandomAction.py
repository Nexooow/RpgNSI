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
        action_rdm=random.choice(self.actions_possibles)
        if isinstance(action_rdm,list):
            actions=list(map(self.jeu.loader.creer_action,action_rdm))
            self.jeu.actions.inserer(actions)
        else:
            action=self.jeu.loader.creer_action(action_rdm)
            self.jeu.actions.inserer([action])
        
        self.complete = True
