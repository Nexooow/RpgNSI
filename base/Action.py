import pygame
from contourpy.util import data

from lib.render import text_render_centered, text_render_centered_left

class Action:
    def __init__(self, jeu, data=None):
        if data is None:
            data = {}
        self.complete = False
        self.jeu = jeu
        self.data = data
        self.desactive_ui = False

    def draw(self):
        pass

    def update(self, events):
        pass

    def executer(self):
        self.complete = False

    def get_complete(self):
        return self.complete


class Dialogue(Action):
    def __init__(self, jeu, data):
        super().__init__(jeu, data)

    def draw(self):
        lines = self.data.get("lines", [])
        speaker = self.data.get("speaker", "")

        if not lines:
            self.complete = True

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
                "imitalic",
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
        super().executer()


class Selection(Action):
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
                    self.jeu.executer_sequence(action)

    def executer(self):
        super().executer()
        self.option_choisie = 0


class Damage(Action):
    def __init__(self, jeu, data):
        super().__init__(jeu, data)

    def executer(self):
        super().executer()
        self.jeu.joueur.infliger(self.data.get("degats", 0))
        self.complete = True

class AjoutTemps(Action):
    
    def __init__ (self, jeu, data):
        super().__init__(jeu, data)
    
    def executer(self):
        super().executer()
        self.jeu.temps += self.data.get("temps", 1)
        self.complete = True
        
class Deplacement(Dialogue):
    
    def __init__ (self, jeu, data):
        data["lines"] = [f"Vous arrivez à {data['lieu']} dans la région {data['region']}."]
        super().__init__(jeu, data)

    def executer(self):
        super().executer()
        self.jeu.region = self.data["region"]
        self.jeu.lieu = self.data["lieu"]
        
class Combat (Action):
    
    def __init__ (self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True
        self.windows = [] # (dmg, start, end)[]
        self.frame = 0
        self.turn = "player" # player/enemy (un seul ennemi max parce que je ne suis pas sadique) (pour l'instant :p)

        vie_max = jeu.joueur.vie_max
        self.player = {
            "vie": vie_max,
            "vie_max": vie_max
        }
        ennemi_data = data["enemy"]
        self.ennemi = {
            "vie_max": ennemi_data["vie"],
            "vie": ennemi_data["vie"],
            "nom": ennemi_data["nom"]
        }
        
    def executer(self):
        super().executer()
        self.jeu.fade = 300
        if "music" in self.data:
            pygame.mixer.music.load(self.data["music"])
            pygame.mixer.music.play(-1)
        
    def update (self, events):
        self.frame += 1
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for window in self.windows:
                    if window[1] < self.frame:
                        self.windows.remove(window)
                        # PARRY (sound, give AP)
    
    def draw_ui (self):

        # ennemi
        ennemi_health_ratio = self.ennemi["vie"] / self.ennemi["vie_max"]
        text_render_centered(self.jeu.ui_surface, self.ennemi["nom"], "regular", (255, 255, 255), (self.jeu.WIDTH / 2, 16), False, 16)
        pygame.draw.rect(self.jeu.ui_surface, (255, 255, 255), (9, 6+20, self.jeu.WIDTH-18, 8))
        pygame.draw.rect(self.jeu.ui_surface, (0, 0, 0), (12, 7+20, self.jeu.WIDTH-24, 6))
        pygame.draw.rect(self.jeu.ui_surface, (179, 32, 21), (12, 7+20, (self.jeu.WIDTH - 24)*ennemi_health_ratio, 6))

        # player
        pygame.draw.rect(self.jeu.ui_surface, (0, 0, 0, 150), (9, 525, self.jeu.WIDTH-9*2, 175-9))

    def draw (self):

        if "background" in self.data:
            # TODO: draw fight background
            pass

        self.draw_ui()


class SelectionAction (Action):

    def __init__ (self, jeu):
        super().__init__(jeu, {})

    def update (self, events):
        pass

    def draw (self):
        pass

    def executer(self):
        super().executer()
        pass
