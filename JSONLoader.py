import json
import os
from random import random, randint
import glob

from Action import Dialogue, Selection

class JSONLoader:
    
    def __init__ (self, parent):
        self.parent = parent
        
        self.actions_sequences = {}
        self.actions_types = {}
        
        self.charger_actions()
        # self.charger_npcs()
                
    def charger_actions (self):
        files = glob.glob("./data/actions/*.json")
        for file in files:
            try:
                with open(file, 'r') as f:
                    content = json.load(f)
                    id = content["id"]
                    type_sequence = content["type"]
                    if type_sequence in self.actions_types.keys():
                        self.actions_types[type_sequence].append(id)
                    else:
                        self.actions_types[type_sequence] = [id]
                    self.actions_sequences[id] = []
                    for action in content['run']:
                        self.actions_sequences[id].append(
                            self.creer_action(action)
                        )
            except Exception:
                continue
        print("Sequences chargées:", self.actions_sequences)
        
    def charger_lieux (self):
        with open("./data/lieux.json", 'r') as f:
            content = json.load(f)
            for lieu in content:
                id = lieu["id"]
                region_nom = lieu["region"]
                region = self.parent.regions[region_nom]
                region.lieux[id] = lieu
                if lieu["entree"]:
                    region.entree = id
                if id not in region.carte.sommet():
                    region.carte.ajout_sommet(id)
                for route in lieu["routes"]:
                    if route["id"] not in region.carte.sommet():
                        region.carte.ajout_sommet(route["id"])
                    if route["bidirectionnel"]:
                        region.carte.ajout_arrete(id, route["id"], route["temps"])
                    else:
                        region.carte.ajout_arc(id, route["id"], route["temps"])
        
    def recuperer_sequence (self, sequence_id):
        if sequence_id in self.actions_sequences.keys():
            return self.actions_sequences[sequence_id]
        else:
            return None
                
    def creer_action (self, data: dict):
        if data["type"] == "dialogue" or data["type"] == "dialog":
            return Dialogue(self.parent, data)
        elif data["type"] == "select":
            return Selection(self.parent, data)

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