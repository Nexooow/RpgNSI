import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from numpy.random.mtrand import f
import pygame

from lib.compatibility import get_canvas_buffer


class Graph:
    def __init__(self, sommets, aretes, orientation=False, pos={}):
        assert isinstance(sommets, list), (
            f"sommets doit être une liste, reçu: {type(sommets)}"
        )
        assert isinstance(aretes, list), (
            f"aretes doit être une liste, reçu: {type(aretes)}"
        )
        self.aretes = aretes
        if not orientation:
            self.aretes = [
                (s2, s1, p)
                for s1, s2, p in self.aretes
                if s1 != s2 and (s2, s1, p) not in self.aretes
            ]
        self.sommets = sommets
        self.pos = pos
        self.orientation = orientation

    def __str__(self):
        return f"Graph ({self.aretes}, {self.sommets}, {self.orientation})"

    def ajout_position(self, sommet, pos):
        self.pos[sommet] = pos

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
        successeurs = []
        for arete in self.aretes:
            if arete[0] == sommet:
                successeurs.append(arete[1])
        return successeurs

    def predecesseur(self, sommet):
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

    def get_graph(self):
        G = nx.DiGraph() if self.orientation else nx.Graph()
        G.add_nodes_from(self.sommets)
        for arrete in self.aretes:
            G.add_edge(
                arrete[0], arrete[1], weight=int(arrete[2]), label=format_temps(int(arrete[2]))
            )
        return G

    def paths(self, a, b) -> tuple[list[str], int]:
        G = self.get_graph()
        chemin = list(nx.shortest_path(G, source=a, target=b, weight="weight"))
        poids = nx.shortest_path_length(G, source=a, target=b, weight="weight")
        return chemin, poids

def format_temps (heures):
    heures = int(heures)
    jours = heures // 24
    heures %= 24
    return f"{f'{jours}j' if jours > 0 else ''}{heures}h"

def affichage_graphe(graph: Graph, screen, image):
    img = plt.imread(f"assets/maps/{image}")
    G = graph.get_graph()

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(img, extent=(0, 1000, 700, 0))
    aretes_labels = {(u, v): format_temps(data['weight']) for u, v, data in G.edges(data=True)}

    nx.draw(
        G,
        graph.pos,
        node_color="none",
        with_labels=True,
        font_family="Arial",
        font_size=10,
        node_size=1000,
    )
    nx.draw_networkx_edge_labels(
        G,
        graph.pos,
        edge_labels=aretes_labels,
        label_pos=0.5,
        rotate=False,
        font_family="Arial",
        bbox=dict(
            facecolor="white", pad=0.2, edgecolor="none"
        ),  # cache l'étiquette derrière le label
    )
    fig.canvas.draw()
    buf = get_canvas_buffer(fig.canvas)
    w, h = fig.canvas.get_width_height()
    image = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
    image = image[..., :3]
    pygame_surface = pygame.surfarray.make_surface(np.transpose(image, (1, 0, 2)))
    plt.close(fig)
    screen.blit(pygame_surface, (0, 0))
