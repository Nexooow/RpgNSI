import pygame
import uuid
import random
import os
import json

from lib.render import text_render_centered
from menu.Menu import Menu

class Accueil (Menu):
    
    def __init__ (self, jeu):
        self.jeu = jeu
        try:
            savesNames = os.listdir("./saves")
            self.saves = [
                json.load(open(f"./saves/{name}", "r")) for name in savesNames
            ]
        except FileNotFoundError:
            self.saves = []
        self.menu_selected_option = 0
        self.particules = []
        self.ouvrir()
        
    def ouvrir (self):
        pygame.mixer.music.load('./assets/music/intro.mp3')
        pygame.mixer.music.set_volume(0.01)
        pygame.mixer.music.play(1, 0, 1000)
        
    def fermer (self):
        pygame.mixer.music.stop()
        
    def update (self, events):
        print("accueil update")
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if self.menu_selected_option != 0:
                    self.menu_selected_option -= 1
                if self.menu_selected_option == 1 and len(self.saves) == 0:
                    self.menu_selected_option = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if self.menu_selected_option != 3:
                    self.menu_selected_option += 1
                if self.menu_selected_option == 1 and len(self.saves) == 0:
                    self.menu_selected_option = 2
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE):
                self.fermer()
                self.jeu.fade = 255
                sound = pygame.mixer.Sound("./assets/sounds/accueil_clique.mp3")
                sound.set_volume(0.25)
                sound.play()
                if self.menu_selected_option == 0:
                    self.jeu.demarrer(str(uuid.uuid4()))
                elif self.menu_selected_option == 1 and len(self.saves) > 0:
                    pass 
                elif self.menu_selected_option == 2:
                    pass
                elif self.menu_selected_option == 3:
                    self.jeu.quitter()
        
        
    def draw (self):
        print("accueil draw")
        doit_generer = True if random.randint(1, 100) == 1 else False
        if doit_generer:
            particule_position = random.randint(0, 1280)
            particule_taille = random.randint(1, 2)
            alpha = random.randint(80, 225)
            self.particules.append(([particule_position, 720], alpha, particule_taille))
        
        for particle in self.particules:
            pygame.draw.circle(self.jeu.fond, (245, 205, 0, particle[1]), particle[0], particle[2])
            particle[0][1] -= 0.25
            if particle[0][1] < 0:
                self.particules.remove(particle)
                    
        text_render_centered(self.jeu.fond, "Game Name", "extrabold", color=(255, 255, 255), pos=(1280/2, 175), size=128)
            
        text_render_centered(self.jeu.fond, "Créer une partie", "regular",
            color = (245, 205, 0, 185),
            pos=(1280/2, 350),
            underline=self.menu_selected_option == 0
        )
        text_render_centered(self.jeu.fond, "Charger une partie", "regular",
            color = (245, 205, 0, 185) if len(self.saves) > 0 else (255-100, 215-100, 0, 140),
            pos=(1280/2, 400),
            underline=self.menu_selected_option == 1
        )
        text_render_centered(self.jeu.fond, "Paramètres", "regular",
            color = (245, 205, 0, 185),
            pos=(1280/2, 450),
            underline=self.menu_selected_option == 2
        )
        text_render_centered(self.jeu.fond, "Quitter", "regular",
            color = (245, 205, 0, 185),
            pos=(1280/2, 500),
            underline=self.menu_selected_option == 3
        )
