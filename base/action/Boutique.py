import pygame
from .Action import Action
class Boutique(Action):
    """
    Action qui ouvre la boutique du jeu, on la fout pour le Wandering Merchant?
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True
        
    def update(self, events):
        self.complete = True

    def draw(self):
        pass

    def executer(self):
        super().executer()
        self.jeu.ouvrir_boutique()