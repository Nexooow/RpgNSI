from lib.graph import Graph, affichage_graphe


class Region:

    def __init__(self, jeu, nom, lieux, image="background"):
        self.jeu = jeu
        self.nom = nom
        self.image = image
        self.entree = None
        self.position = self.jeu.carte.pos[self.nom]
        self.modificateur_chance = 1

        routes = set()
        self.lieux = {}

        for lieu in lieux:
            identifiant = lieu["id"]
            assert isinstance(identifiant,
                              str), f"ID de lieu doit être une chaîne de caractères, mais est {type(identifiant)}"
            self.lieux[identifiant] = lieu

            if "entree" in lieu and lieu["entree"]:
                self.entree = identifiant

            for route in lieu["routes"]:
                routes.add((identifiant, route["id"], route["temps"]))
                if route["bidirectionnel"]:
                    routes.add((route["id"], identifiant, route["temps"]))

        self.carte = Graph([nom for nom in self.lieux.keys()], list(routes), True,
                           {f'{lieu["id"]}': (lieu["location"]["x"], lieu["location"]["y"]) for lieu in lieux})

    def afficher(self):
        affichage_graphe(self.carte, self.jeu.ui_surface, self.image)
