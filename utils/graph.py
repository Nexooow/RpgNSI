import networkx as nx
import matplotlib.pyplot as plt


class Graph:

    def __init__(self, sommets, aretes, orientation=False):
        self.aretes = aretes
        self.sommets = sommets
        self.orientation = orientation

    def __str__(self):
        return f"Graph ({self.aretes}, {self.sommets}, {self.orientation})"

    def ajout_arc(self, sommet1, sommet2):
        self.aretes.append((sommet1, sommet2))

    def ajout_arete(self, sommet1, sommet2):
        self.ajout_arc(sommet1, sommet2)
        self.ajout_arc(sommet2, sommet1)

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
        G = nx.DiGraph() if self.orientation else nx.Graph()
        G.add_nodes_from(self.sommets)
        G.add_edges_from(self.aretes)
        nx.draw_networkx(G, node_color="skyblue", with_labels=True)
        plt.show()
