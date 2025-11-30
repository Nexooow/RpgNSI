import pygame

from lib.graph import Graph
from Action import Action
from JSONLoader import JSONLoader
from lib.file import File
from menu.accueil import Accueil

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
    "Elder Tree": (500, 230),
}

class Jeu:

    def __init__ (self):
        
        self.running = True
        self.statut = "accueil"
        self.accueil = Accueil(self)
        self.clock = pygame.time.Clock()
        
        self.fond = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.filter_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        
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
        self.regions = {}
        self.region = None
        self.lieu = None
        
        # temps
        self.jour = 1
        self.heure = 12
        self.minute = 0
        
        # filtres pour affichage
        self.fade = 0
        
    def demarrer (self, id: str, json = None):
        self.statut = "jeu"
        self.accueil.fermer()
        self.identifiant = id
        
    def save (self):
        pass
        
    def quitter (self):
        self.running = False
        
    def gerer_evenement (self, evenements):
        if self.statut == "accueil":
            self.accueil.update(evenements)
        else:
            if self.action_actuelle is not None:
                self.action_actuelle.update(evenements)
            
    def executer_sequence (self, id):
        sequence = self.loader.actions_sequences[id]
        for action in sequence:
            self.actions.enfiler(action)
            
    def executer (self):
        action = self.action_actuelle
        if action is None:
            if not self.actions.est_vide():
                self.action_actuelle = self.actions.defiler()
                assert self.action_actuelle is not None
                self.action_actuelle.executer(self)
        else:
            if action.est_complete():
                if not self.actions.est_vide():
                    self.action_actuelle = self.actions.defiler()
                    assert self.action_actuelle is not None
                    self.action_actuelle.executer(self)
                else:
                    self.action_actuelle = None
                    
    def scene (self):
        if self.statut == "accueil":
            self.accueil.draw()
        elif self.statut == "jeu":
            if self.action_actuelle is not None:
                self.action_actuelle.draw()
            self.ui()
        self.filters() # applique les filtres sur l'écran
        
    def ui (self):
        pygame.draw.rect(self.fond, (255, 255, 255), self.fond.get_rect())
        pygame.draw.rect(self.fond, (0, 0, 255), (8, 8, 90, 90))
        
    def filters (self):
        if self.fade > 0:
            pygame.draw.rect(self.filter_surface, (0, 0, 0, self.fade), self.filter_surface.get_rect())
            self.fade -= 5
        elif self.fade <= 0:
            self.fade = 0
        
    def deplacement (self, destination, est_region = False):
        if est_region: # est une region
            pass
        else: # est un lieu
            pass