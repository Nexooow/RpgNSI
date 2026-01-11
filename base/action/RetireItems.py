import pygame
from .Action import Action
class RetireItems(Action):
    """
    Action qui retire des items à l'inventaire du joueur.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.items = data.get("items", [])
    def executer(self):
        super().executer()
        for item in self.items:
            self.jeu.equipe.retirer_item(item["id"], item.get("quantite", 1))
        self.complete = True
