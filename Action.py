import pygame

from lib.render import text_render_centered, text_render_centered_left


class Action:
    def __init__(self, jeu, json={}):
        self.complete = False
        self.jeu = jeu
        self.json = json
        self.desactive_ui = False

    def draw(self):
        pass

    def update(self, events):
        pass

    def executer(self):
        pass

    def get_complete(self):
        return self.complete


class Dialogue(Action):
    def __init__(self, jeu, json):
        super().__init__(jeu, json)

    def draw(self):
        lines = self.json.get("lines", [])
        speaker = self.json.get("speaker", "")

        if not lines:
            return

        # hauteur boite
        line_height = 30
        padding = 20
        speaker_height = 35 if speaker else 0
        total_height = len(lines) * line_height + padding * 2 + speaker_height

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
        if speaker:
            text_render_centered_left(
                self.jeu.ui_surface,
                speaker,
                "imregular",
                color=(255, 200, 100),
                pos=(box_x + padding, current_y),
                size=26,
            )
            current_y += speaker_height

        for line in lines:
            text_render_centered_left(
                self.jeu.ui_surface,
                line,
                "imregular",
                color=(255, 255, 255),
                pos=(box_x + padding, current_y),
                size=24,
            )
            current_y += line_height

        # fleche
        indicator_x = box_x + box_width - 30
        indicator_y = box_y + total_height - 15
        triangle_points = [
            (indicator_x, indicator_y - 5),
            (indicator_x + 10, indicator_y),
            (indicator_x, indicator_y + 5),
        ]
        pygame.draw.polygon(self.jeu.ui_surface, (255, 255, 255), triangle_points)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.complete = True

    def executer(self):
        pass


class Selection(Action):
    def __init__(self, jeu, json):
        super().__init__(jeu, json)
        self.option_choisie = 0

    def draw(self):
        options = self.json.get("options", [])
        question = self.json.get("question", "")

        if not options:
            self.complete = True
            return

        line_height = 35
        padding = 20
        question_height = 40 if question else 0
        total_height = len(options) * line_height + question_height + padding * 2

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

        if question:
            text_render_centered_left(
                self.jeu.ui_surface,
                question,
                "imregular",
                color=(255, 255, 255),
                pos=(box_x + padding, current_y + 15),
                size=26,
            )
            current_y += question_height

        for index, choix in enumerate(options):
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

        instruction_y = box_y + total_height + 30
        text_render_centered(
            self.jeu.ui_surface,
            "↑↓ pour naviguer - ESPACE pour sélectionner",
            "imregular",
            color=(150, 150, 150),
            pos=(500, instruction_y),
            size=18,
        )

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if self.option_choisie > 0:
                    self.option_choisie -= 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if self.option_choisie < len(self.json["options"]) - 1:
                    self.option_choisie += 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.complete = True
                valeur = self.json["options"][self.option_choisie]["valeur"]
                print(self.json["actions"][valeur])

    def executer(self):
        self.option_choisie = 0


class Damage(Action):
    def __init__(self, jeu, json):
        super().__init__(jeu, json)

    def executer(self):
        self.jeu.joueur.infliger(self.json["degats"])
        self.complete = True
