from matplotlib.backend_bases import LocationEvent
import pygame
from lib.graph import affichage_graphe
from menu.Menu import Menu

class Carte (Menu):
    
    def __init__ (self, jeu):
        self.jeu = jeu
        self.region = None
        
    def update (self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.fermer()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = event.pos
                if self.region is None: # graphe global
                    for region_name, region in self.jeu.regions.items():
                        region_position = region.position
                        if pygame.Rect((region_position[0]-50, region_position[1]-50, 150, 150)).collidepoint(position):
                            self.region = region_name
                else:   
                    region = self.jeu.regions[self.region]
                    for lieu_nom, lieu in region.lieux.items():
                        location = lieu["location"]
                        if pygame.Rect((location["x"]-50, location["y"]-50, 150, 150)).collidepoint(position):
                            self.fermer()
                            self.jeu.deplacement(self.region, lieu_nom)
                        
    def fermer (self):
        self.jeu.fermer_menu()
        
    def draw (self):
        if self.region is None:
            affichage_graphe(self.jeu.carte, self.jeu.ui_surface, "background.webp")
        else:
            self.jeu.regions[self.region].afficher()