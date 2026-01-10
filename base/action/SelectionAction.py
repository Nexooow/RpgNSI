import pygame

from menu.carte import Carte
from menu.inventaire import Inventaire
from menu.competences import MenuCompetences
from .Action import Action
from lib.render import text_render_centered_left
from lib.sounds import son_selection


class SelectionAction(Action):
    """
    Action éxécutée lorsqu'il n'y a plus d'actions dans la file, et lorsque le joueur doit choisir
    ce qu'il veut faire.
    Exemple: ouvrir la carte, ouvrir l'inventaire...
    """

    def __init__(self, jeu, _):
        super().__init__(jeu, {"type": "selection-action"})
        self.option_choisie = 0
        self.options = []

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.option_choisie == 0:
                    self.complete = True
                    self.jeu.interagir()
                elif self.option_choisie == 1:
                    self.jeu.ouvrir_menu(Inventaire(self.jeu))
                elif self.option_choisie == 2:
                    self.jeu.ouvrir_menu(Carte(self.jeu))
                elif self.option_choisie == 3:
                    self.jeu.ouvrir_menu(MenuCompetences(self.jeu))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                son_selection.play()
                self.option_choisie = (self.option_choisie + 1) % len(self.options)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                son_selection.play()
                self.option_choisie = (self.option_choisie - 1) % len(self.options)

    def draw(self):

        line_height = 35
        padding = 20
        total_height = len(self.options) * line_height + padding * 2

        # position boite
        box_width = 960
        box_x = 20
        box_y = 700 - total_height - 20

        pygame.draw.rect(
            self.jeu.ui_surface,
            (50, 50, 50),
            (box_x - 3, box_y - 3, box_width + 6, total_height + 6),
        )
        pygame.draw.rect(
            self.jeu.ui_surface, (30, 30, 40), (box_x, box_y, box_width, total_height)
        )

        current_y = box_y + padding

        for index, choix in enumerate(self.options):
            est_choisi = index == self.option_choisie

            if est_choisi:
                highlight_rect = (
                    box_x + 10,
                    current_y - 5,
                    box_width - 20,
                    line_height - 5,
                )
                pygame.draw.rect(self.jeu.ui_surface, (70, 70, 90), highlight_rect)
                pygame.draw.rect(
                    self.jeu.ui_surface, (100, 150, 200), highlight_rect, 2
                )

            color = (255, 255, 255) if est_choisi else (200, 200, 200)
            text_render_centered_left(
                self.jeu.ui_surface,
                choix,
                "imregular",
                color=color,
                pos=(box_x + padding, current_y + 12),
                size=24,
            )

            current_y += line_height

    def executer(self):
        super().executer()
        if self.jeu.debute: self.jeu.sauvegarder()
        self.options = [
            f"Intéragir avec {self.jeu.lieu}",
            "Ouvrir l'inventaire",
            "Ouvrir la carte",
            "Gérer les compétences",
        ]
