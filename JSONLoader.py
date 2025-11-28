import json
import os
from random import random
import Action

class JSONLoader:

    actions: dict()

    evenements_positifs: list()
    evenements_negatifs: list()
    evenements_neutres: list()
    
    def __init__ (self, parent):
        self.parent = parent
        actionsFiles = os.listdir("./data/actions")
        for actionName in actionsFiles:
            try:
                content = json.load(os.read(f"./data/actions/{actionName}"))
                self.actions[content["id"]] = Action(content)
            except FileNotFoundError:
                continue

        npcsFiles = os.listdir("./data/npcs")
        for npcName in npcsFiles:
            try:
                content = json.load(os.read(f"./data/npcs/{npcName}"))
            except FileNotFoundError:
                continue


    def tirer_action (self, chance, chance_negative):
        evenement = random()*100 <= chance
        if evenement:
            positive_part = ((chance-chance_negative)/0.75)+chance_negative
            rand = random()*100
            if rand <= chance_negative:
                index = random(0, len(self.evenements_negatifs))
                key = self.evenements_negatifs[index]
                return self.actions[key]
            if rand >= positive_part:
                index = random(0, len(self.evenements_positifs))
                key = self.evenements_positifs[index]
                return self.actions[key]
            else:
                index = random(0, len(self.evenements_positifs))
                key = self.evenements_positifs[index]
                return self.actions[key]
            

