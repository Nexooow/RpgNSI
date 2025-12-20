from glob import glob
import json
from random import randint, random

from base.Action import Dialogue, Selection, AjoutTemps, Damage, Deplacement, Combat
from base.Region import Region

class JSONLoader:
    def __init__(self, parent):
        self.parent = parent

        self.actions_sequences = {}
        self.actions_types = {}

        self.charger_actions()
        self.charger_regions()

    def charger_actions(self):
        files = glob("./.data/actions/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    assert isinstance(content, dict)
                    identifiant = content["id"]
                    type_sequence = content["type"]
                    if type_sequence in self.actions_types.keys():
                        self.actions_types[type_sequence].append(identifiant)
                    else:
                        self.actions_types[type_sequence] = [identifiant]
                    self.actions_sequences[identifiant] = []
                    for action in content["run"]:
                        self.actions_sequences[identifiant].append(self.creer_action(action))
                    print(f"Séquence '{identifiant}' chargée ({len(self.actions_sequences[identifiant])} actions)")
            except Exception:
                print(f"impossible de charger la séquence '{file}'")
                continue

    def charger_regions(self):
        lieux_json = self.charger_lieux()
        regions = {}
        for lieu in lieux_json:
            if lieu["region"] not in regions:
                regions[lieu["region"]] = [lieu]
            else:
                regions[lieu["region"]].append(lieu)
        return {
            "Auberge": Region(self.parent, "Auberge", regions["Auberge"]),
            "Mountain": Region(
                self.parent, "Mountain", regions["Mountain"], image="mountain"
            ),
            "Ceilidh": Region(self.parent, "Ceilidh", regions["Ceilidh"], image="ceilidh"),
            "Dawn of the world": Region(
                self.parent, "Dawn of the world", regions["Dawn of the world"]
            ),
            "Elder Tree": Region(self.parent, "Elder Tree", regions["Elder Tree"]),
        }

    def charger_lieux(self):
        with open("./.data/lieux.json", "r") as f:
            content = json.load(f)
            assert isinstance(content, list)
            return content
        
    def charger_npcs (self):
        files = glob("./.data/actions/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file) as f:
                    content = json.load(f)
                    assert isinstance(content, dict)
            except Exception:
                continue

    def recuperer_sequence(self, sequence_id):
        if sequence_id in self.actions_sequences.keys():
            return self.actions_sequences[sequence_id]
        else:
            return None

    def creer_action(self, data: dict):
        actions = {
            "dialogue": Dialogue,
            "select": Selection,
            "damage": Damage,
            "ajout-temps": AjoutTemps,
            "deplacement": Deplacement,
            "combat": Combat
        }
        try:
            return actions[data["type"]](self.parent, data) # instancie l'action correspondante
        except KeyError:
            return None

    def tirer_action(self, chance):
        evenement = random() * 100 <= chance
        if evenement:
            if randint(0, 100) <= chance:
                key = self.actions_types["event-positif"][
                    randint(0, len(self.actions_types["event-positif"]) - 1)
                ]
            else:
                key = self.actions_types["event"][
                    randint(0, len(self.actions_types["event"]) - 1)
                ]
            return key
        else:
            return None
