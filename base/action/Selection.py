import pygame
from lib.render import text_render_centered_left
from .Action import Action


class Selection(Action):
    """
    Propose une séléction à l'utilisateur et execute une action selon le choix.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.option_choisie = 0
        self.options = self.data.get("options", [])
        self.question = self.data.get("question", "")

    def draw(self):

        if not self.options:
            self.complete = True
            return

        line_height = 35
        padding = 20
        question_height = 40 if self.question else 0
        total_height = len(self.options) * line_height + question_height + padding * 2

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

        if self.question:
            text_render_centered_left(
                self.jeu.ui_surface,
                self.question,
                "imregular",
                color=(255, 255, 255),
                pos=(box_x + padding, current_y + 15),
                size=24,
            )
            current_y += question_height

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
                choix.get("name", ""),
                "imregular",
                color=color,
                pos=(box_x + padding, current_y + 12),
                size=24,
            )

            current_y += line_height

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if self.option_choisie > 0:
                    self.option_choisie -= 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if self.option_choisie < len(self.options) - 1:
                    self.option_choisie += 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.complete = True
                valeur = self.options[self.option_choisie]["valeur"]
                action = self.data["actions"][valeur]
                if isinstance(action, str):
                    self.jeu.executer_sequence(action, True)
                elif isinstance(action, list):
                    # insérer les actions juste après l'action de selection
                    self.jeu.actions.inserer(list(map(self.jeu.loader.creer_action, action)))

    def executer(self):
        super().executer()
        self.option_choisie = 0
