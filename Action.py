import pygame

class Action:
    data: dict()
    complete: False
    indexAction: -1 # l'index de la sous action en cours d'utilisation, -1: l'action n'est pas lancée

    def __init__ (self, json):
        assert isinstance(json, dict)
        self.json = json;
        self.nom = json["nom"]

    def executer (self):
        runner = self.json["run"]
        if not runner:
            return;
        action_actuelle = runner[self.indexAction]
        if not action_actuelle:
            self.complete = True
            return
        
        
    def update (self):
        pass

    def draw (self):
        pass

    def est_complete (self):
        return False; 
