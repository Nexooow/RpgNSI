import pygame
from lib.graph import affichage_graphe
from menu.Menu import Menu


class Carte(Menu):

    def __init__(self, jeu):
        super().__init__(jeu)
        self.region = None

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.fermer()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = event.pos
                if self.region is None:  # graphe global
                    for region_name, region in self.jeu.regions.items():
                        position = region.position
                        if pygame.Rect((position[0] - 50, position[1] - 50, 150, 150)).collidepoint(mouse_position):
                            self.region = region_name
                else:
                    region = self.jeu.regions[self.region]
                    for lieu_nom, lieu in region.lieux.items():
                        if lieu_nom == self.jeu.lieu:
                            continue
                        location = lieu["location"]
                        if pygame.Rect((location["x"] - 50, location["y"] - 50, 150, 150)).collidepoint(mouse_position):
                            self.fermer()
                            self.jeu.deplacement(self.region, lieu_nom)

    def draw(self):
        if self.region is None:
            affichage_graphe(self.jeu.carte, self.jeu.ui_surface, "background")
        else:
            self.jeu.regions[self.region].afficher()
