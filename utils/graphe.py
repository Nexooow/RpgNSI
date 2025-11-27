import networkx as nx
import matplotlib.pyplot as plt
import base64
import numpy as np
import pygame
from io import BytesIO

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
    def sommets(self):
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
def def_graph(graphe):
    G=nx.DiGraph() if graphe.orientation else nx.Graph()
    G.add_edges_from(graphe.aretes_tuple)
    G.add_nodes_from(graphe.sommets)
    return G
def affichage_graphe(graphe,b64,pos):
    img_bytes = base64.b64decode(b64)
    img = plt.imread(BytesIO(img_bytes), format='webp')
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(img,extent=[0,1000,700,0])
    G=def_graph(graphe)
    nx.draw(G,pos,node_color ="none", with_labels =True ,node_size = 1000)
    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    pygame_surface = pygame.surfarray.make_surface(np.transpose(image, (1, 0, 2)))
    plt.close(fig)
    return pygame_surface
def paths(graphe,a,b):
    G=def_graph(graphe)
    path=list(nx.all_simple_paths(G,a,b,cutoff=None))
    pathway={i:len(path[i]) for i in range(len(path))}
    return path[min(pathway,key=pathway.get)]
graphe=Graph([("Auberge","B"),("B","Ceilidh"),("B","Auberge"),("Ceilidh","B"),("Ceilidh","Auberge"),("Auberge","Elder Tree"),("Auberge","Ceilidh")],["Auberge","B","Ceilidh","Dawn of the world","Elder Tree"],True)
graphe.ajout_arc("Auberge","Dawn of the world") if not graphe.orientation else graphe.ajout_arete("Auberge","Dawn of the world")
#le truc b64
pygame.init()
screen = pygame.display.set_mode((1000, 700))
background = affichage_graphe(graphe,b64,pos = {"Auberge": (200, 400), "B": (600, 120),"Ceilidh": (660, 480),"Dawn of the world": (450, 500),"Elder Tree": (500, 230)})
screen.blit(background,(0,0))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
pygame.quit()
