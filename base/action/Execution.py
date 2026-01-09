from .Action import Action
import pygame

class Execution(Action):

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        assert "code" in self.data

    def executer(self):
        super().executer()
        exec(self.data.get("code"), {"jeu": self.jeu, "pygame": pygame})
        self.complete = True
