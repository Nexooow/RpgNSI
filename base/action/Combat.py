import pygame
import random
from lib.render import text_render_centered, text_render_centered_left
from .Action import Action
from lib.file import File

parrysound = pygame.mixer.Sound("assets/sounds/parry.mp3")
parrysound.set_volume(0.05)


class Combat(Action):
    """
    Combat au tour par tour.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True

        self.action = "demarrage"  # demarrage/selection/attaque
        self.tour_actuel = None
        self.tours = File()

        self.ennemis = data.get("ennemis", [])
        self.personnages = []

        self.menu_actuel = None  # None/principal/competences/items
        self.selection = 0

    def maj_tours(self):
        self.tours.contenu = []
        combatants = []

        for personnage in self.personnages:
            if personnage["vie"] <= 0:
                continue
            combatants.append({
                "index": self.personnages.index(personnage),
                "type": "personnages",
                "vitesse": personnage["vitesse"]
            })
        for ennemi in self.ennemis:
            if ennemi["vie"] <= 0:
                continue
            combatants.append({
                "index": self.ennemis.index(ennemi),
                "type": "ennemis",
                "vitesse": ennemi.get("vitesse", 0)
            })

        combatants.sort(key=lambda x: (x.get("vitesse", 0), x["type"] == "personnages"), reverse=True)

        for combatant in combatants:
            self.tours.enfiler((combatant["type"], combatant["index"]))

    def executer(self):
        for personnage in self.jeu.equipe.personnages:
            self.personnages.append({
                "nom": personnage.nom,
                "vie": personnage.vie,
                "vie_max": personnage.vie_max,
                "force": personnage.force,
                "vitesse": personnage.vitesse,
                "arme": self.jeu.loader.items.get(personnage.arme, None),
                "effets": {},  # key: nom effet, val: (niveau, durée)
                "competences": [
                    {**competence, "id": id_competence}
                    for id_competence, competence in personnage.competences.items()
                    if id_competence in personnage.competences_debloques
                ]  # filtre les compétences pour ne renvoyer que les competences débloquées
            })

        self.maj_tours()
        self.tour_actuel = self.tours.defiler()

    def update(self, events):
        if self.tour_actuel[0] == "ennemis":
            pass
        elif self.tour_actuel[0] == "personnages" and self.action == "selection":
            perso_actuel = self.personnages[self.tour_actuel[1]]

            if self.menu_actuel == "principal":  # menu principal (selection du type d'action)
                for event in events:

                    max_selection = 1 if "silence" not in perso_actuel.effets else 2
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % max_selection
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % max_selection
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        match self.selection:
                            case 0:
                                self.action = "attaque"
                            case 1:
                                self.action = "items"
                            case 2:
                                self.action = "competences"

    def draw(self):
        pass
