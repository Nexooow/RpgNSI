import pygame

from .Action import Action

from menu.carte import Carte
from menu.inventaire import Inventaire

from lib.render import text_render_centered_left


class Deplacement(Action):
    """
    Action éxécutée lorsque le joueur a fini son déplacement ou atteint un point intermédiaire dans son déplacement.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, {**data, "type": "deplacement"})
        self.option_choisie = 0
        self.options = []

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.data["destination"]:
                    self.complete = True
                else:
                    match self.option_choisie:
                        case 0:
                            self.complete = True
                        case 1:
                            self.jeu.actions.contenu = []
                            self.complete = True
                        case 2:
                            self.jeu.ouvrir_menu(Inventaire(self.jeu))
                        case 3:
                            self.jeu.ouvrir_menu(Carte(self.jeu))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.option_choisie = (self.option_choisie + 1) % len(self.options)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.option_choisie = (self.option_choisie - 1) % len(self.options)

    def draw(self):

        if not self.data["destination"]:

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

        else:

            # hauteur boite
            line_height = 30
            padding = 20
            total_height = line_height + padding * 2

            # position boite
            box_y = 700 - total_height - 20
            box_width = 960
            box_x = 20

            pygame.draw.rect(
                self.jeu.ui_surface,
                (50, 50, 50),
                (box_x - 3, box_y - 3, box_width + 6, total_height + 6),
            )
            pygame.draw.rect(
                self.jeu.ui_surface, (20, 20, 30), (box_x, box_y, box_width, total_height)
            )

            current_y = box_y + padding

            text_render_centered_left(
                self.jeu.ui_surface,
                "Vous êtes arrivé à destination.",
                "imregular",
                color=(255, 255, 255),
                pos=(box_x + padding, current_y),
                size=24,
            )

            # fleche
            indicator_x = box_x + box_width - 30
            indicator_y = box_y + total_height - 15
            triangle_points = [
                (indicator_x, indicator_y - 5),
                (indicator_x + 10, indicator_y),
                (indicator_x, indicator_y + 5),
            ]
            pygame.draw.polygon(self.jeu.ui_surface, (255, 255, 255), triangle_points)

    def executer(self):
        super().executer()
        self.jeu.lieu = self.data["lieu"]
        self.jeu.region = self.data["region"]

        if self.jeu.debute: self.jeu.sauvegarder()

        self.options = [
            "Continuer le trajet",
            "Interrompre le trajet",
            "Ouvrir l'inventaire",
            # "Gérer votre équipe",
            "Ouvrir la carte"
        ]
