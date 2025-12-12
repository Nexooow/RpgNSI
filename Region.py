from types import LambdaType
from lib.graph import Graph, affichage_graphe


class Region:
    def __init__(self, jeu, nom, lieux, image="background.webp"):
        self.jeu = jeu
        self.nom = nom
        self.image = image
        self.entree = None
        self.position = self.jeu.carte.pos[self.nom]

        routes = set()
        self.lieux = {lieu["id"]: lieu for lieu in lieux}
        for lieu in lieux:
            id = lieu["id"]
            assert isinstance(id, str), f"ID de lieu doit être une chaîne de caractères, mais est {type(id)}"
            if "entree" in lieu and lieu["entree"]:
                self.entree = id
            for route in lieu["routes"]:
                routes.add((id, route["id"], route["temps"]))
                if route["bidirectionnel"]:
                    routes.add((route["id"], id, route["temps"]))
        self.carte = Graph([lieu["id"] for lieu in lieux], list(routes), True, {f'{lieu["id"]}':(lieu["location"]["x"], lieu["location"]["y"]) for lieu in lieux})

    def afficher(self):
        affichage_graphe(self.carte, self.jeu.ui_surface, self.image)
