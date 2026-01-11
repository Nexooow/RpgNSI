import pygame
import random
from lib.render import text_render_centered, text_render_centered_left,render_text_wrapped
from menu.Menu import Menu
from lib.file import File
import Jeu

total_height = 200
box_y = 700 - total_height - 20
box_width = 960
box_x = 20
couleur_hightlight = (70, 70, 90)

separator_x = box_x + 400

menu_width = box_width - (separator_x - box_x)

DESCRIPTION_RECT = pygame.Rect(
    100,
    300,
    menu_width - 40,
    total_height
)
class MenuCompetences(Menu):

    def __init__(self, jeu):
        super().__init__(jeu)
        self.options = []
        self.perso_selectionne = None
        self.displaying = False
        self.description_text = ""
        self.choice = None
        self.menu_actuel = "principal"
        self.selection = 0

    def ouvrir(self):
        self.menu_actuel = "principal"

    def changer_menu(self, menu):
        self.menu_actuel = menu
        self.selection = 0

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.options:
                    if event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % len(self.options)
        self.update_selection(events)

    def update_selection(self, events):
        if self.menu_actuel == "principal":
            self.options = range(len(self.jeu.equipe.personnages))
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.perso_selectionne = self.jeu.equipe.personnages[self.selection]
                        self.changer_menu(self.perso_selectionne.nom)
                    elif event.key == pygame.K_ESCAPE:
                        self.fermer()


        elif self.menu_actuel == self.perso_selectionne.nom:
            self.options = self.perso_selectionne.competences_equipes
            if not self.options:
                self.changer_menu("principal")
                return
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.choice = self.selection
                        self.changer_menu("competences possibles")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "competences possibles":
            # prix_accessible permet de recuperer un dico des competences achetables avec le budget

            prix_accessible = {
                competence: self.perso_selectionne.competences[competence]
                for competence in self.perso_selectionne.competences.keys()
                if competence not in self.perso_selectionne.competences_equipes and (self.perso_selectionne.competences[competence][
                        "points"] <= self.perso_selectionne.points_competences or (
                            competence in self.perso_selectionne.competences_achetees and not competence in self.perso_selectionne.competences_equipes))
            }
            self.options = list(prix_accessible.keys())
            
            print(self.options)
            print(self.selection)
            if not self.options:
                self.changer_menu("principal")
                return
            competence_selectionnee = list(prix_accessible.keys())[self.selection]
            self.description_text = self.perso_selectionne.competences[competence_selectionnee]
            self.displaying=True
            # self.options=self.perso_selectionne.competences
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Si le nb de competences equipees n'excede pas 4 on ajoute la competence selectionnee, autrement on la fait remplacer celle selectionnee precedemment
                        if len(self.perso_selectionne.competences_equipes) <= 3:
                            self.perso_selectionne.competences_equipes += [competence_selectionnee]
                        else:

                            self.perso_selectionne.competences_equipes[self.choice] = competence_selectionnee
                        self.perso_selectionne.competences_achetees.append(competence_selectionnee)
                        self.perso_selectionne.points_competences-=1
                        self.changer_menu(self.perso_selectionne.nom)
                    elif event.key == pygame.K_ESCAPE:
                        if self.displaying:
                            self.displaying = False
                            self.description_text = ""
                        self.changer_menu("principal")

    def draw_selection(self, options):
        option_height = total_height / len(options)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == self.selection else (200, 200, 200)

            text_render_centered_left(
                self.jeu.ui_surface,
                option,
                "bold" if i == self.selection else "regular",
                color,
                (separator_x + 20, box_y + i * option_height + option_height / 2),
                size=22
            )

    def draw(self):
        if self.menu_actuel == "principal":
            options = [perso.nom for perso in self.jeu.equipe.personnages]
            self.draw_selection(options)
        elif self.menu_actuel == self.perso_selectionne.nom:
            options = self.perso_selectionne.competences_equipes
            self.draw_selection(options)
        elif self.menu_actuel == "competences possibles":
            """
            competences = self.perso_selectionne.competences
            self.draw_selection([comp["nom"] for comp in competences.values()])
            """
            self.draw_selection(self.options)
            if self.displaying:
                """
                text_render_centered(
                    self.jeu.ui_surface,
                    f"{self.description_text}",
                    "regular",
                    (230, 230, 230),
                    (500, 350),
                    size=18
                )
                """
                render_text_wrapped(
                    self.jeu.ui_surface,
                    self.description_text["description"],
                    font_name="regular",
                    rect=DESCRIPTION_RECT
                )

