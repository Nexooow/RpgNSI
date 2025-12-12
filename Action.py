import pygame

from lib.render import text_render_centered


class Action:
    def __init__(self, jeu, json={}):
        self.complete = False
        self.jeu = jeu
        self.json = json
        self.desactive_ui = False

    def __repr__(self):
        return str(self.json)

    def draw(self):
        """
        Méthode pour dessiner l'action sur l'écran.
        Retourne une erreur si la méthode n'est pas implémentée.
        """
        raise NotImplementedError("La méthode draw n'est pas implémentée")

    def update(self, events):
        """
        Méthode pour dessiner l'action sur l'écran.
        Retourne une erreur si la méthode n'est pas implémentée.
        """
        raise NotImplementedError("La méthode update n'est pas implémentée")

    def executer(self):
        """
        Méthode pour dessiner l'action sur l'écran.
        Retourne une erreur si la méthode n'est pas implémentée.
        """
        raise NotImplementedError("La méthode executer n'est pas implémentée")

    def est_complete(self):
        return self.complete


class Dialogue(Action):
    def __init__(self, jeu, json):
        super().__init__(jeu, json)
        self.frame_relative = -100  # -100 = "l'action" est en train d'être démarrée, 0 = "l'action" est en cours d'exécution, 100 = "l'action" est terminée

    def draw(self):
        pygame.draw.rect(self.jeu.ui_surface, (0, 0, 0, 15), (16, 650-(len(self.json["lines"])*26), 1000-32, 650))
        for index, line in enumerate(self.json["lines"]):
            text_render_centered(
                self.jeu.ui_surface,
                line,
                "imregular",
                (0, 0, 0, 255),
                (1000 / 2, 675 - index * 26),
                size=28,
            )

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.complete = True

    def executer(self):
        self.frame_relative = -100


class Selection(Action):
    def __init__(self, jeu, json):
        super().__init__(jeu, json)
        self.option_choisie = 0

    def draw(self):
        reversed_options = self.json["options"][::-1]
        for index, choix in enumerate(reversed_options):
            text_render_centered(
                self.jeu.ui_surface,
                str(choix["name"]) + str(index),
                "regular",
                pos=(1000 / 2, 650 - (50 * index)),
                underline=index == self.option_choisie,
            )
        text_render_centered(
            self.jeu.ui_surface,
            self.json["question"],
            "bold",
            pos=(1000 / 2, 650 - (50 * len(reversed_options))),
        )

    def update(self, events):
        pass

    def executer(self):
        pass
