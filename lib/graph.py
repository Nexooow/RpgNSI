import matplotlib.pyplot as plt
import networkx as nx

class Graph:
    def __init__(self, sommets, aretes, pos, orientation=False, image="background.webp"):
        self.aretes = aretes
        if not orientation:
            self.aretes = [(s2, s1, p) for s1, s2, p in self.aretes if s1 != s2 and (s2, s1, p) not in self.aretes]
        self.sommets = sommets
        self.pos = pos
        self.orientation = orientation
        self.image = image

    def __str__(self):
        return f"Graph ({self.aretes}, {self.sommets}, {self.orientation})"

    def ajout_arc(self, sommet1, sommet2, poids=0):
        self.aretes.append((sommet1, sommet2, poids))

    def ajout_arete(self, sommet1, sommet2, poids=0):
        self.ajout_arc(sommet1, sommet2, poids)
        self.ajout_arc(sommet2, sommet1, poids)

    def sommet(self):
        return self.sommets

    def arete(self):
        return self.aretes

    def voisins(self, sommet):
        voisins = []
        for arete in self.aretes:
            if arete[0] == sommet:
                voisins.append(arete[1])
            elif arete[1] == sommet:
                voisins.append(arete[0])
        return voisins

    def successeur(self, sommet):
        assert not self.orientation, "Le graphe n'est pas orienté"
        successeurs = []
        for arete in self.aretes:
            if arete[0] == sommet:
                successeurs.append(arete[1])
        return successeurs

    def predecesseur(self, sommet):
        assert not self.orientation, "Le graphe n'est pas orienté"
        predecesseurs = []
        for arete in self.aretes:
            if arete[1] == sommet:
                predecesseurs.append(arete[0])
        return predecesseurs

    def degre_sommet(self, sommet):
        return len(self.voisins(sommet))

    def complet(self):
        somme_degres = sum(self.degre_sommet(sommet) for sommet in self.sommets)
        # un graphe est complet quand la somme des degrés de tous les sommets est égale au double du nombre d'arêtes
        return somme_degres == 2 * len(self.aretes)

    def affichage(self):
        img = plt.imread(f"assets/{self.image}.webp")
        G = nx.DiGraph() if self.orientation else nx.Graph()

        G.add_nodes_from(self.sommets)
        for arrete in self.aretes:
            G.add_edge(arrete[0], arrete[1], weight=arrete[2], label=arrete[2])

        _, ax = plt.subplots(figsize=(10, 7))
        ax.imshow(img, extent=(0, 1000, 700, 0))
        aretes_labels = {
            (u, v): f"{data['weight']}h" for u, v, data in G.edges(data=True)
        }

        nx.draw(
            G,
            self.pos,
            node_color="none",
            with_labels=True,
            font_family="Arial",
            font_size=10,
            node_size=1000,
        )
        nx.draw_networkx_edge_labels(
            G,
            self.pos,
            edge_labels=aretes_labels,
            label_pos=0.5,
            rotate=False,
            font_family="Arial",
            bbox=dict(
                facecolor="white", pad=0.2, edgecolor="none"
            ) # cache l'étiquette derrière le label
        )
        plt.show()


if __name__ == "__main__":
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
    pos = {
        "Auberge": (200, 400),
        "Mountain": (600, 120),
        "Ceilidh": (660, 480),
        "Dawn of the world": (450, 500),
        "Elder Tree": (500, 230),
    }
    graph = Graph(
        sommets,
        aretes,
        pos,
        True,
        "background.webp"
    )
