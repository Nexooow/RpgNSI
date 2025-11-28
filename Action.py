import pygame

class Action:
    data: dict()

    def __init__ (self, json):
        assert isinstance(json, dict)
        self.json = json;
        self.nom = json["nom"]

    def executer (self):
        pass

    def draw (self):
        pass

    def est_complete (self):
        return False; 
