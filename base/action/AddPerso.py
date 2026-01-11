import pygame
from .Action import Action
class AddPerso(Action):
#Action qui ajoute un perso à la team
    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.perso_data=data.get("perso_data", {})
    def executer(self):
        super().executer()
        from base.Personnage import Barman, Fachan
        nouveau_perso=Barman if self.perso_data=="Barman" else Fachan
        self.jeu.personnages.ajouter_personnage(nouveau_perso(self.jeu.equipe))
        self.complete=True