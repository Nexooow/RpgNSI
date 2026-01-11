import json
import os
import random
import uuid

import pygame

from lib.render import text_render_centered
from menu.Menu import Menu
from lib.sounds import son_selection

son_clique = pygame.mixer.Sound("./assets/sounds/accueil_clique.mp3")
son_clique.set_volume(0.25)


class Accueil(Menu):
    def __init__(self, jeu):
        super().__init__(jeu)

        try:
            saves_names = os.listdir("./.data/saves")
            self.saves = [
                json.load(open(f"./.data/saves/{name}", "r")) for name in saves_names
            ]
        except FileNotFoundError:
            self.saves = []

        self.menu_selected_option = 0
        self.sous_page = "main"
        self.particules = []
        self.ouvrir()

    def ouvrir(self):
        self.jeu.jouer_musique("intro", loop=True, volume=0.01)
        self.jeu.fade = 255

    def fermer(self):
        pygame.mixer.music.stop()
        super().fermer()

    def update_page_main(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if self.menu_selected_option != 0:
                    self.menu_selected_option -= 1
                if self.menu_selected_option == 1 and len(self.saves) == 0:
                    self.menu_selected_option = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if self.menu_selected_option != 2:
                    self.menu_selected_option += 1
                if self.menu_selected_option == 1 and len(self.saves) == 0:
                    self.menu_selected_option = 2
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE):
                if self.menu_selected_option == 0:
                    self.jeu.fade = 500
                    sound = pygame.mixer.Sound(
                        "./assets/sounds/accueil_clique.mp3")
                    sound.set_volume(0.10)
                    self.fermer()
                    sound.play()
                    self.jeu.demarrer(str(uuid.uuid4()))
                elif self.menu_selected_option == 1 and len(self.saves) > 0:
                    print("ouvrir sauvegardes")
                    self.menu_selected_option = 0
                    self.sous_page = "sauvegardes"
                elif self.menu_selected_option == 2:
                    self.jeu.quitter()

    def update_page_sauvegardes(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.menu_selected_option -= 1
                if self.menu_selected_option == -1:
                    self.menu_selected_option = len(self.saves) - 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.menu_selected_option += 1
                if self.menu_selected_option == len(self.saves):
                    self.menu_selected_option = 0
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE):
                self.fermer()
                self.jeu.fade = 255
                son_clique.play()
                partie_choisie = self.saves[self.menu_selected_option]
                assert isinstance(partie_choisie, dict)
                self.jeu.demarrer(partie_choisie["id"], partie_choisie)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and (
                    event.key == pygame.K_UP or event.key == pygame.K_DOWN
            ):
                son_selection.play()
        if self.sous_page == "main":
            self.update_page_main(events)
        elif self.sous_page == "sauvegardes":
            self.update_page_sauvegardes(events)

    def draw_main(self):
        text_render_centered(
            self.jeu.fond,
            "Game Name",
            "extrabold",
            color=(255, 255, 255),
            pos=(1000 / 2, 175),
            size=128,
        )

        text_render_centered(
            self.jeu.fond,
            "Créer une partie",
            "regular",
            color=(245, 205, 0, 185),
            pos=(1000 / 2, 350),
            underline=self.menu_selected_option == 0,
        )
        text_render_centered(
            self.jeu.fond,
            "Charger une partie",
            "regular",
            color=(245, 205, 0, 185)
            if len(self.saves) > 0
            else (255 - 100, 215 - 100, 0, 140),
            pos=(1000 / 2, 400),
            underline=self.menu_selected_option == 1,
        )
        text_render_centered(
            self.jeu.fond,
            "Quitter",
            "regular",
            color=(245, 205, 0, 185),
            pos=(1000 / 2, 450),
            underline=self.menu_selected_option == 2,
        )

    def draw_sauvegardes(self):
        text_render_centered(
            self.jeu.fond,
            "Sauvegardes",
            "bold",
            color=(255, 255, 255),
            pos=(1000 / 2, 175),
            size=86,
        )

        for index, save in enumerate(self.saves):
            jours, heures = divmod(save["temps"], 24)
            text_render_centered(
                self.jeu.fond,
                f"{jours} {heures:02d}h - {save['region']} {save['lieu']}",
                "regular",
                color=(245, 205, 0, 185),
                pos=(1000 / 2, 175 + 25 + 50 * (index + 1)),
                underline=self.menu_selected_option == index,
            )

    def draw(self):
        doit_generer = True if random.randint(1, 100) == 1 else False
        if doit_generer:
            particule_position = random.randint(0, 1000)
            particule_taille = random.randint(1, 2)
            alpha = random.randint(80, 225)
            self.particules.append(
                ([particule_position, 700], alpha, particule_taille))

        for particle in self.particules:
            pygame.draw.circle(
                self.jeu.fond, (245, 205, 0, particle[1]), particle[0], particle[2]
            )
            particle[0][1] -= 0.25
            if particle[0][1] < 0:
                self.particules.remove(particle)

        if self.sous_page == "main":
            self.draw_main()
        elif self.sous_page == "sauvegardes":
            self.draw_sauvegardes()
