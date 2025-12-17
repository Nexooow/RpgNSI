from glob import glob
import json
from random import randint, random

from Action import Dialogue, Selection
from Region import Region

class JSONLoader:
    def __init__(self, parent):
        self.parent = parent

        self.actions_sequences = {}
        self.actions_types = {}

        self.charger_actions()
        self.charger_regions()

    def charger_actions(self):
        files = glob("./data/actions/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    assert isinstance(content, dict)
                    id = content["id"]
                    type_sequence = content["type"]
                    if type_sequence in self.actions_types.keys():
                        self.actions_types[type_sequence].append(id)
                    else:
                        self.actions_types[type_sequence] = [id]
                    self.actions_sequences[id] = []
                    for action in content["run"]:
                        self.actions_sequences[id].append(self.creer_action(action))
                    print(f"Séquence '{id}' chargée ({len(self.actions_sequences[id])} actions)")
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
                self.parent, "Mountain", regions["Mountain"], image="mountain.jpg"
            ),
            "Ceilidh": Region(self.parent, "Ceilidh", regions["Ceilidh"], image="ceilidh.jpg"),
            "Dawn of the world": Region(
                self.parent, "Dawn of the world", regions["Dawn of the world"]
            ),
            "Elder Tree": Region(self.parent, "Elder Tree", regions["Elder Tree"]),
        }

    def charger_lieux(self):
        with open("./data/lieux.json", "r") as f:
            content = json.load(f)
            assert isinstance(content, list)
            return content
        
    def charger_npcs (self):
        files = glob("./data/actions/**/*.json", recursive=True)
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
        if data["type"] == "dialogue" or data["type"] == "dialog":
            return Dialogue(self.parent, data)
        elif data["type"] == "select":
            return Selection(self.parent, data)

    def tirer_action(self, chance, chance_negative):
        evenement = random() * 100 <= chance
        if evenement:
            positive_part = ((chance - chance_negative) / 0.75) + chance_negative
            rand = random() * 100
            if rand <= chance_negative:
                events_negatif = self.actions_types["negatif"]
                index = randint(0, len(events_negatif)-1)
                key = events_negatif[index]
            if rand >= positive_part:
                events_positifs = self.actions_types["positif"]
                index = randint(0, len(events_positifs)-1)
                key = events_positifs[index]
            else:
                events_neutre = self.actions_types["neutre"]
                index = randint(0, len(events_neutre)-1)
                key = events_neutre[index]
            return key
        else:
            return None
