import json
import os
from random import random, randint

from NPC import NPC
from Action import Action

class JSONLoader:
    
    def __init__ (self, parent):
        self.parent = parent
        
        self.actions = {}
        self.npcs = {}
        
        self.charger_actions()
        self.charger_npcs()
                
    def charger_actions (self):
        actionsFiles = os.listdir("./data/actions")
        for actionName in actionsFiles:
            try:
                with open(f"./data/actions/{actionName}", 'r') as file:
                    content = json.load(file)
                    if isinstance(content, dict):
                        self.actions[content["id"]] = Action(content)
                    elif isinstance(content, list):
                        for action_json in content:
                            self.actions[action_json["id"]] = Action(action_json)
            except Exception:
                continue
                
    def charger_npcs (self):
        npcsFiles = os.listdir("./data/npcs")
        for npcName in npcsFiles:
            try:
                with open(f"./data/npcs/{npcName}", 'r') as file:
                    content = json.load(file)
                    self.npcs[content["id"]] = NPC(content)
            except Exception:
                continue

    def tirer_action (self, chance, chance_negative):
        evenement = random()*100 <= chance
        if evenement:
            positive_part = ((chance-chance_negative)/0.75)+chance_negative
            rand = random()*100
            if rand <= chance_negative:
                pass
                #index = randint(0, len(self.evenements_negatifs))
                #key = self.evenements_negatifs[index]
                #return self.actions[key]
            if rand >= positive_part:
                pass
                #index = randint(0, len(self.evenements_positifs))
                #key = self.evenements_positifs[index]
                #return self.actions[key]
            else:
                pass
                #index = randint(0, len(self.evenements_positifs))
                #key = self.evenements_positifs[index]
                #return self.actions[key]
        else:
            return None