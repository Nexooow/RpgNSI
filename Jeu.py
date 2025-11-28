from PIL.TiffImagePlugin import SAMPLEFORMAT
from lib.graph import Graph
from JSONLoader import JSONLoader
from lib.file import File

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

    def __init__ (self, id: str, json: dict = None):
        
        self.identifiant = id
        
        self.loader = JSONLoader(self)
        self.scene_actuelle = None
        self.scenes = File()
        
        self.carte = Graph(
            sommets,
            aretes,
            positions_sommets,
            True,
            "background.webp"
        )
        
        self.regions = {}
        self.region = json["emplacement"]["region"] or "Auberge"
        self.lieu = json["emplacement"]["lieu"] or self.regions[self.region].lieu_depart
        
        self.jour = 1
        self.heure = 12
        self.minute = 0

    def gerer_evenement (self, evenement):
        pass

    def scene (self, screen):
        pass
        
    def deplacement (self, lieu, est_region = False):
        pass
        
    def save (self):
        pass