from glob import glob
import json
from random import randint, random

from base.action import Action, actions_par_type
from base.Region import Region


class JSONLoader:
    def __init__(self, parent):
        self.parent = parent

        self.actions_sequences = {}
        self.actions_types = {}

        self.npc = {}
        self.items = {}

    def charger(self):
        self.charger_actions()
        self.charger_items()
        self.charger_npc()

    def creer_sequence(self, identifiant, actions, type_sequence=None):
        if type_sequence is None:
            type_sequence = "action"  # type par défault

        if type_sequence in self.actions_types.keys():
            self.actions_types[type_sequence].append(identifiant)
        else:
            self.actions_types[type_sequence] = [identifiant]

        self.actions_sequences[identifiant] = []
        for action in actions:
            assert isinstance(action, dict)
            assert "type" in action
            self.actions_sequences[identifiant].append(self.creer_action(action))

    def charger_actions(self):
        files = glob("./.data/actions/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:

                    content = json.load(f)
                    assert isinstance(content, dict)
                    assert "run" in content and "id" in content
                    identifiant = content["id"]
                    type_sequence = content["type"]

                    self.creer_sequence(identifiant, content["run"], type_sequence)

                    print(
                        f"Loader | Actions | séquence '{identifiant}' chargée ({len(self.actions_sequences[identifiant])} actions)")

            except Exception as e:
                print(f"impossible de charger la séquence '{file}': {e}")
                continue

    def charger_items(self):
        files = glob("./.data/items/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    assert isinstance(content, dict)
                    self.items[content["id"]] = content
                    print(f"Loader | Items | {content['id']} chargé")
            except Exception as e:
                print(f"Impossible de charger l'item '{file}': {e}")
                continue

    def charger_regions(self):
        lieux_json = self.charger_lieux()
        regions = {}
        for lieu in lieux_json:
            print(f"Loader | Lieux | {lieu['region']} > {lieu["id"]}")
            region = lieu["region"]  # la région du lieux
            if region not in regions:
                regions[region] = [lieu]
            else:
                regions[region].append(lieu)
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
            try:
                content = json.load(f)
                assert isinstance(content, list)
                return content
            except Exception as e:
                print(f"Impossible de charger les lieux: {e}")

    def charger_npc(self):
        files = glob("./.data/npc/**/*.json", recursive=True)
        for file in files:
            try:
                with open(file) as f:
                    content = json.load(f)
                    assert isinstance(content, dict)
                    self.npc[content["id"]] = content
                    if "rencontre" in content and content["rencontre"]:
                        # sequence premiere interaction
                        self.creer_sequence(f"{content["id"]}:rencontre", content["rencontre"], "action")
                    self.creer_sequence(f"{content['id']}:interaction", content["interaction"], "action")
            except Exception:
                continue

    def get_sequence(self, sequence_id: str) -> list[Action] | None:
        if sequence_id in self.actions_sequences.keys():
            return self.actions_sequences[sequence_id]
        else:
            return None

    def creer_action(self, data: dict) -> Action | None:
        try:
            return actions_par_type[data["type"]](self.parent, data)  # instancie l'action correspondante
        except KeyError:
            print(f"Action inconnue: {data["type"]}")
            return None

    def tirer_action(self, chance: int) -> str | None:
        evenement = random() * 100 <= 15
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
