import pygame
import math

from lib.file import File
from lib.graph import Graph

from boss.radahn import Radahn

from menu.carte import Carte
from menu.accueil import Accueil

from Action import Action
from JSONLoader import JSONLoader
from Joueur import Joueur
from Region import Region

sommets = ["Auberge", "Mountain", "Ceilidh", "Dawn of the world", "Elder Tree"]
aretes = [
    ("Auberge", "Mountain", 0),
    ("Mountain", "Ceilidh", 0),
    ("Mountain", "Auberge", 0),
    ("Ceilidh", "Mountain", 0),
    ("Ceilidh", "Auberge", 0),
    ("Auberge", "Elder Tree", 0),
    ("Auberge", "Ceilidh", 0),
    ("Auberge", "Dawn of the world", 0)
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
        
        # affichage
        self.loader = JSONLoader(self)
        self.action_actuelle: Action | None = None
        self.actions = File()

        # carte et regions/lieux
        self.carte = Graph(
            sommets,
            aretes,
            positions_sommets,
            True,
            "background.webp"
        )
        self.lieux_visite = set()
        self.regions = {
            "Auberge": Region(self, "Auberge"),
            "Mountain": Region(self, "Mountain", image="mountain.jpg"),
            "Ceilidh": Region(self, "Ceilidh", image="ceilidh.jpg"),
            "Dawn of the world": Region(self, "Dawn of the world"),
            "Elder Tree": Region(self, "Elder Tree")
        }
        self.region = None
        self.lieu = self.region.entree if self.region else None
        
        # temps
        self.jour = 1
        self.heure = 12
        self.minute = 0
        
        # filtres pour affichage
        self.fade = 0
        
    def region_actuelle (self):
        if self.region is None:
            return None
        return self.regions[self.region]
        
    def demarrer (self, id: str, json = None):
        self.statut = "jeu"
        self.menu = None
        self.identifiant = id
        self.joueur = Joueur(self, json)
        self.executer_sequence("test")
        #self.ajouter_action(Radahn(self))
        
    def save (self):
        pass
        
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
        if self.statut == "jeu":
            self.fond.fill((255, 255, 255))
            if self.action_actuelle is not None:
                self.action_actuelle.draw()
            self.ui()
        self.filters() # applique les filtres sur l'écran
        
        
    def ui (self):
        if self.action_actuelle is not None:
            if not self.action_actuelle.desactive_ui:
                pygame.draw.rect(self.fond, (255, 255, 255), self.fond.get_rect())
                pygame.draw.rect(self.fond, (0, 0, 255), (8, 8, 90, 90))
        
    def filters (self):
        if self.fade > 0:
            pygame.draw.rect(
                self.filter_surface,
                (0, 0, 0, min([self.fade, 255])),
                self.filter_surface.get_rect()
            )
            self.fade -= 4
        elif self.fade <= 0:
            self.fade = 0
        
    def deplacement (self, region, lieu):
        region_actuelle = self.region_actuelle()
        assert region_actuelle is not None
        temps_deplacement = 0
        if self.region == region:
            if self.lieu == lieu:
                return
            deplacement_region = region_actuelle.carte.paths(self.lieu, lieu)
            temps_deplacement += deplacement_region[1]
        else:
            deplacement_regions = self.carte.paths(self.region, region)
            temps_deplacement += deplacement_regions[1]
            if not (lieu == self.regions[region].entree):
                deplacement_lieu = self.regions[region].carte.paths(self.regions[region].entree, lieu)
                temps_deplacement += deplacement_lieu[1]
        print(f"Temps de déplacement : {temps_deplacement} secondes")