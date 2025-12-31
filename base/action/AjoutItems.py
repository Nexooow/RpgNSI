import pygame
from .Action import Action


class AjoutItems(Action):
    """
    Action qui ajoute des items à l'inventaire du joueur.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.items = data.get("items", [])

    def update(self, events):
        self.complete = True

    def draw(self):
        pass

    def executer(self):
        super().executer()
        for item in self.items:
            self.jeu.equipe.ajouter_item(item["item_id"], item.get("quantity", 1))
