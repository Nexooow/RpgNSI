import pygame
import math
import json

from typing_extensions import NoDefault

from lib.file import File
from lib.graph import Graph

from boss.radahn import Radahn

from lib.render import text_render_centered, text_render_centered_left, text_render_centered_up
from menu.carte import Carte
from menu.accueil import Accueil

from Action import Action
from JSONLoader import JSONLoader
from Joueur import Joueur
from Region import Region

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
    ("Dawn of the world", "Auberge", 19)
]
positions_sommets = {
    "Auberge": (200, 400),
    "Mountain": (600, 120),
    "Ceilidh": (660, 480),
    "Dawn of the world": (450, 500),
    "Elder Tree": (500, 260),
}

class Jeu:

    def __init__ (self):
        
        self.running = True
        self.statut = "accueil" # accueil/jeu/deplacement
        self.menu = Accueil(self)
        self.clock = pygame.time.Clock()
        
        self.fond = pygame.Surface((1000, 700), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((1000, 700), pygame.SRCALPHA)
        self.filter_surface = pygame.Surface((1000, 700), pygame.SRCALPHA)

        # carte et regions/lieux
        self.carte = Graph(
            sommets,
            aretes,
            True,
            positions_sommets
        )
        self.lieux_visite = set()
        
        self.loader = JSONLoader(self)
        self.action_actuelle: Action | None = None
        self.actions = File()
        
        self.regions = self.loader.charger_regions()
        self.region = None
        self.lieu = self.region.entree if self.region else None
        
        self.temps = 0
        
        # filtres pour affichage
        self.fade = 300
        
    def obtenir_temps (self):
        heures = self.temps // 60
        jours = heures // 24
        heures %= 24
        return jours, heures
        
    def region_actuelle (self):
        if self.region is None:
            return None
        return self.regions[self.region]
        
    def demarrer (self, id: str, json: dict | None = None):
        self.statut = "jeu"
        self.menu = None
        self.identifiant = id
        self.joueur = Joueur(self, json["joueur"] if json and "joueur" in json else None)
        if json is not None: 
            self.restaurer(json)
        else:
            self.region = "Auberge"
            self.lieu = self.regions["Auberge"].entree
            self.executer_sequence("test")
        self.save()
        
    def restaurer (self, json):
        self.region = json["region"]
        self.lieu = self.regions[self.region]
        self.temps = json["temps"]
        if json["actions"]:
            for action in json["actions"]:
                action_instance = self.loader.creer_action(action)
                self.ajouter_action(action_instance)
        if json["action_actuelle"]:
            self.action_actuelle = self.loader.creer_action(json["action_actuelle"])
            
        
    def save (self):
        data = {
            "id": self.identifiant,
            "joueur": self.joueur.save(),
            "temps": self.temps
        }
        json.dump(data, open(f"./saves/{self.identifiant}.json", "w"))
        
    
    def quitter (self):
        self.running = False
        
    def gerer_evenement (self, evenements):
        if self.menu is not None:
            self.menu.update(evenements)
        if self.statut == "jeu":
            for event in evenements:
                if self.menu is None:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                        self.ouvrir_menu(Carte(self))
            if self.action_actuelle is not None:
                self.action_actuelle.update(evenements)
            
    def ajouter_action (self, action):
        assert isinstance(action, Action)
        self.actions.enfiler(action)
        
    def executer_sequence (self, id):
        sequence = self.loader.recuperer_sequence(id)
        if sequence:
            for action in sequence:
                self.ajouter_action(action)
    
    def fermer_menu (self):
        self.menu = None
                
    def ouvrir_menu (self, menu):
        self.menu = menu
        self.menu.ouvrir()
            
    def executer (self):
        action = self.action_actuelle
        if action is None:
            if not self.actions.est_vide():
                self.action_actuelle = self.actions.defiler()
                assert self.action_actuelle is not None
                self.action_actuelle.executer()
        else:
            if action.est_complete():
                if not self.actions.est_vide():
                    self.action_actuelle = self.actions.defiler()
                    assert self.action_actuelle is not None
                    self.action_actuelle.executer()
                else:
                    self.action_actuelle = None
                    
    def scene (self):
        if self.menu is not None:
            self.menu.draw()
        elif self.statut == "jeu":
            self.fond.fill((255, 255, 255))
            if self.action_actuelle is not None:
                self.action_actuelle.draw()
            self.ui()
        self.filters() # applique les filtres sur l'écran
        
        
    def ui (self):
        if self.action_actuelle is not None:
            if not self.action_actuelle.desactive_ui:
                (jour, heure) = self.obtenir_temps()
                # écris le temps en haut à gauche
                pygame.draw.rect(self.fond, (0, 0, 255), (8, 8, 90, 90))
                pygame.draw.rect(self.fond, (255, 0, 0), (8+90/2, 8+90/2, 5, 5))
                text_render_centered_left(self.ui_surface, f"Jour {jour} | {heure}h", "regular", pos=(10, 8+90/2))

        
    def filters (self):
        if self.fade > 0:
            if self.fade < 10:
                self.fade = 2
            pygame.draw.rect(
                self.filter_surface,
                (0, 0, 0, min([self.fade, 255])),
                self.filter_surface.get_rect()
            )
            self.fade -= 2
        
    def ajouter_temps (self, heures):
        self.heure += heures
        if self.heure >= 24:
            self.jour += self.heure // 24
            self.heure %= 24
        
    def deplacement (self, region, lieu):

        region_actuelle = self.region_actuelle()
        assert region_actuelle is not None
        temps_deplacement = 0
        
        print(f"deplacement vers {region}/{lieu}")
        print(f"depuis {region_actuelle.nom}/{self.lieu}")
        
        if region != region_actuelle.nom: # destination dans une autre région
            
            if self.lieu != region_actuelle.entree: # se déplacer d'abord vers l'entrée de la région pour en sortir
                temps_deplacement += region_actuelle.carte.paths(self.lieu, region_actuelle.entree)[1]
                
            temps_deplacement += self.carte.paths(region_actuelle.nom, region)[1]
            
            region_destination = self.regions[region]
            if lieu != region_destination.entree:
                # si le lieu de destination n'est pas l'entrée de la région
                # s'y déplacer.
                temps_deplacement += region_destination.carte.paths(region_destination.entree, lieu)[1]
            
        else: # si le lieu de destination est dans la région actuelle
            
            chemin = self.carte.paths(self.lieu, lieu)
            temps_deplacement += chemin[1]
        
        print(f"temps du trajet : {temps_deplacement}")
        
        self.lieu = lieu
        self.region = region