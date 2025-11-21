# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 18:37:38 2025

@author: peter
"""
import networkx as nx
import matplotlib.pyplot as plt

class Graph:

    def __init__(self,aretes,sommets,orientation):
        self.sommets=sommets
        self.orientation=orientation
        if not self.orientation:
            for i in list(set(aretes)):
                aretes+=[(i[1],i[0])]
        self.aretes_tuple=list(set(aretes))
        
        self.aretes={}
        for arete in self.aretes_tuple:
            key,value=arete
            if key not in self.aretes:
                self.aretes[key]=[value]
            else:
                self.aretes[key].append(value)
        
    def __str__(self):
        graph=[[1  if self.sommets[j] in self.aretes.get(self.sommets[i],[]) else 0 for j in range(len(self.sommets))] for i in range(len(self.sommets))]
        return f"{graph}"

    def ajout_arete(self,s1,s2):
        self.aretes_tuple+=[(s1,s2)]
        if s1 in self.aretes.keys():
            self.aretes[s1]+=[s2]
            
        else:
            self.aretes[s1]=[s2]
            
    def ajout_arc(self,s1,s2):
        self.ajout_arete(s1,s2)
        self.ajout_arete(s2,s1)

    def get_sommets(self):
        return self.sommets

    def aretes(self):
        return self.aretes_tuple

    def voisin(self,nom_sommet):
        return self.aretes[nom_sommet]

    def predecesseur(self,nom_sommet):
        return [i[0] for i in self.aretes_tuple if i[1]==nom_sommet]

    def successeur(self,nom_sommet):
        return [i[1] for i in self.aretes_tuple if i[0]==nom_sommet]

    def degre_sommet(self,nom_sommet):
        return len(self.aretes[nom_sommet])

    def connexe(self):
        for i in self.sommets:
            if i not in self.aretes.keys():
                return False
        return True

    def complet(self):
        for i in self.sommets:
            if len(set(self.aretes[i]))!=len(self.sommets)-1:
                return False
        return True

def affichage_graphe(graphe):
    G=nx.DiGraph() if graphe.orientation else nx.Graph()
    G.add_edges_from(graphe.aretes_tuple)
    G.add_nodes_from(graphe.sommets)
    nx.draw(G, node_color ="skyblue", with_labels =True ,node_size = 1000)
    plt.show()

