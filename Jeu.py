import json
import pygame

from base.Action import Action, Deplacement, AjoutTemps
from base.Joueur import Joueur
from base.JSONLoader import JSONLoader

from lib.file import File
from lib.graph import Graph
from lib.render import text_render_centered

from menu.accueil import Accueil
from menu.carte import Carte

sommets = ["Auberge", "Mountain", "Ceilidh", "Dawn of the world", "Elder Tree"]
aretes = [
    ("Auberge", "Mountain", 45),
    ("Mountain", "Ceilidh", 33),
    ("Mountain", "Auberge", 45),
    ("Mountain", "Elder Tree", 12),
    ("Ceilidh", "Mountain", 33),
    ("Ceilidh", "Auberge", 34),
    ("Auberge", "Elder Tree", 25),
    ("Auberge", "Ceilidh", 34),
    ("Auberge", "Dawn of the world", 19),
    ("Dawn of the world", "Auberge", 19),
]
positions_sommets = {
    "Auberge": (200, 400),
    "Mountain": (600, 120),
    "Ceilidh": (660, 480),
    "Dawn of the world": (450, 500),
    "Elder Tree": (500, 260),
}

class Jeu:

    WIDTH = 1000
    HEIGHT = 700

    def __init__(self):

        self.running = True
        self.statut = "accueil"  # accueil/jeu/deplacement
        self.menu = Accueil(self)
        self.clock = pygame.time.Clock()

        self.fond = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.filter_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        self.joueur = None
        self.identifiant = None

        # carte et regions/lieux
        self.carte = Graph(sommets, aretes, True, positions_sommets)
        self.lieux_visite = set()

        self.loader = JSONLoader(self)
        self.action_actuelle: Action | None = None
        self.actions = File()

        self.regions = self.loader.charger_regions()
        self.region = None
        self.lieu = self.region.entree if self.region else None

        self.temps = 24 + 12

        # filtres pour affichage
        self.fade = 300

    # GETTERS

    def get_temps(self):
        return divmod(self.temps, 24) # retourne (temps//24, temps%24) donc (jour, heure)

    def get_region_actuelle(self):
        if self.region is None:
            return None
        return self.regions[self.region]

    # GESTION PARTIES

    def demarrer(self, identifiant, save_json=None):
        self.statut = "jeu"
        self.menu = None
        self.identifiant = identifiant
        self.joueur = Joueur(
            self, save_json["joueur"] if save_json and "joueur" in save_json else None
        )
        if save_json is not None:
            self.restaurer(save_json)
        else:
            self.region = "Auberge"
            self.lieu = self.regions["Auberge"].entree
            self.executer_sequence("debut")
            #self.ajouter_action(Combat(self, {
            #    "enemy": {
            #        "nom": "test",
            #        "vie": 100
            #    }
            #}))
            #self.ajouter_action(Radahn(self)) # test radahn
        self.sauvegarder()

    def restaurer(self, save_json):
        self.region = save_json["region"]
        self.lieu = self.regions[self.region]
        self.temps = save_json["temps"]
        if save_json["actions"]:
            for action in save_json["actions"]:
                action_instance = self.loader.creer_action(action)
                self.ajouter_action(action_instance)
        if save_json["action_actuelle"]:
            self.action_actuelle = self.loader.creer_action(save_json["action_actuelle"])
            self.action_actuelle.executer()

    def sauvegarder(self):
        actions = [action.data for action in self.actions.contenu]
        data = {
            "id": self.identifiant,
            "joueur": self.joueur.sauvegarder(),
            "temps": self.temps,
            "region": self.region,
            "lieu": self.lieu,
            "actions": actions,
            "action_actuelle": self.action_actuelle.data if self.action_actuelle else None
        }
        print(data)
        json.dump(data, open(f"./.data/saves/{self.identifiant}.json", "w"))

    def quitter(self):
        self.running = False

    # AFFICHAGE, ÉVÉNEMENTS ET GESTION DES ACTIONS

    def gerer_evenement(self, evenements):
        if self.menu is not None:
            self.menu.update(evenements)
        if self.statut == "jeu":
            for event in evenements:
                if self.menu is None:
                    if (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_m
                        and self.action_actuelle is None
                    ):
                        self.ouvrir_menu(Carte(self))
            if self.action_actuelle is not None:
                self.action_actuelle.update(evenements)

    def executer(self):
        action = self.action_actuelle
        if action is None:
            if not self.actions.est_vide():
                self.action_actuelle = self.actions.defiler()
                assert self.action_actuelle is not None
                self.action_actuelle.executer()
        else:
            if action.get_complete():
                if not self.actions.est_vide():
                    self.action_actuelle = self.actions.defiler()
                    assert self.action_actuelle is not None
                    self.action_actuelle.executer()
                else:
                    self.action_actuelle = None

    def scene(self):
        if self.menu is not None:
            self.menu.draw()
        elif self.statut == "jeu":
            self.fond.fill((255, 255, 255))
            if self.action_actuelle is not None:
                self.action_actuelle.draw()
            self.ui()
        self.filters()  # applique les filtres sur l'écran

    def ui(self):
        if not self.action_actuelle or (
            self.action_actuelle and not self.action_actuelle.desactive_ui
        ):
            (jour, heure) = self.get_temps()

            # dimensions boite
            box_width = 220
            box_height = 50
            box_x = 15
            box_y = 15

            # bordure
            pygame.draw.rect(
                self.fond,
                (40, 40, 50),
                (box_x - 2, box_y - 2, box_width + 4, box_height + 4),
            )
            pygame.draw.rect(
                self.fond, (25, 25, 35), (box_x, box_y, box_width, box_height)
            )

            # séparateur
            center_x = box_x + box_width // 2
            pygame.draw.line(
                self.fond,
                (100, 100, 120),
                (center_x, box_y + 8),
                (center_x, box_y + box_height - 8),
                1,
            )

            text_render_centered(
                self.ui_surface,
                f"Jour {jour}",
                "imregular",
                color=(200, 200, 255),
                pos=(box_x + box_width // 4, box_y + box_height // 2),
                size=22,
            )

            heure_format = f"{heure:02d}:00"
            text_render_centered(
                self.ui_surface,
                heure_format,
                "imregular",
                color=(255, 255, 200),
                pos=(box_x + 3 * box_width // 4, box_y + box_height // 2),
                size=22,
            )

    def filters(self):
        if self.fade > 0:
            if self.fade < 10:
                self.fade = 2
            pygame.draw.rect(
                self.filter_surface,
                (0, 0, 0, min([self.fade, 255])),
                self.filter_surface.get_rect(),
            )
            self.fade -= 2
            
    def ajouter_action(self, action):
        assert isinstance(action, Action), f"L'action à ajouter n'est pas une instance de la classe Action"
        self.actions.enfiler(action)

    def executer_sequence(self, identifiant):
        sequence = self.loader.recuperer_sequence(identifiant)
        if sequence:
            for action in sequence:
                self.ajouter_action(action)

    # GESTION MENU

    def fermer_menu(self):
        self.menu = None

    def ouvrir_menu(self, menu):
        self.menu = menu
        self.menu.ouvrir()

    # DEPLACEMENTS

    def calcul_temps_deplacement (self, region, lieu):
        temps_deplacement = 0
        region_actuelle = self.get_region_actuelle()
        if region != region_actuelle.nom:  # destination dans une autre région
            if (
                self.lieu != region_actuelle.entree
            ):  # se déplacer d'abord vers l'entrée de la région pour en sortir
                temps_deplacement += region_actuelle.carte.paths(
                    self.lieu, region_actuelle.entree
                )[1]
            temps_deplacement += self.carte.paths(region_actuelle.nom, region)[1]
            region_destination = self.regions[region]
            if lieu != region_destination.entree:
                # si le lieu de destination n'est pas l'entrée de la région
                # s'y déplacer.
                temps_deplacement += region_destination.carte.paths(
                    region_destination.entree, lieu
                )[1]
        else:  # si le lieu de destination est dans la région actuelle
            chemin = self.carte.paths(self.lieu, lieu)
            temps_deplacement += chemin[1]

        return temps_deplacement

    def deplacement(self, region, lieu):

        region_actuelle = self.get_region_actuelle()
        assert region_actuelle is not None

        print(f"deplacement vers {region}/{lieu}")
        print(f"depuis {region_actuelle.nom}/{self.lieu}")

        temps_deplacement = self.calcul_temps_deplacement(region, lieu)
        simulation_temps = self.temps

        for heure in range(temps_deplacement):

            chance = self.joueur.chance
            jour_sim, heure_sim = divmod(simulation_temps, 24)
            if heure_sim <= 5 or heure_sim >= 22: # moins de chance pendant la nuit
                chance = chance * 0.75
            # TODO: chance différente selon la région

            sequence = self.loader.tirer_action(
                chance
            )
            if sequence is not None:
                self.executer_sequence(sequence)

            simulation_temps += 1
            self.ajouter_action(AjoutTemps(self, { "temps": 1 })) # permet l'ajout de temps progressivement

        print(f"temps du trajet : {temps_deplacement}")

        self.ajouter_action(Deplacement(self, { "region": region, "lieu": lieu }))
