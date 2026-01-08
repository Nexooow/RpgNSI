import pygame
import random
from lib.render import text_render_centered, text_render_centered_left
from .Action import Action
from lib.file import File

parrysound = pygame.mixer.Sound("assets/sounds/parry.mp3")
parrysound.set_volume(0.05)

total_height = 200
box_y = 700 - total_height - 20
box_width = 960
box_x = 20
couleur_hightlight = (70, 70, 90)

separator_x = box_x + 400

menu_width = box_width - (separator_x - box_x)


def instance_combat(personnage):
    """
    Convertit le personnage en instance utilisable pour le combat (ajout d'attributs nécessaires; effets ...)
    """
    return {
        "type": "personnage",
        **personnage.__dict__,
        "effets": [],  # cle: nom de l'effet, valeur : (niveau, durée)
        "pa": 3,
        "competences": [
            {**competence, "id": id_competence}
            for id_competence, competence in personnage.competences.items()
            if id_competence in personnage.competences_equipes
        ]
    }


def transformer_ennemi(ennemi):
    """
    Transforme un ennemi en instance utilisable pour le combat (ajout des effets et attributs si manquants)
    """
    instance = {
        "type": "ennemi",
        **ennemi,
        "effets": []
    }
    if "attributs" not in ennemi:
        instance["attributs"] = {}
    return instance


class Combat(Action):
    """
    Combat au tour par tour.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True

        self.musique = data.get("musique", None)
        self.utilise_musique = self.musique is not None

        self.tours = File()
        self.tour = None
        self.action = None
        self.options = []

        self.ennemis = [transformer_ennemi(ennemi) for ennemi in data["ennemis"]]
        self.personnages = []

        self.attaques = []
        self.sub_frame_count = None

        self.menu_actuel = "principal"
        self.selection = 0

        self.action_en_cours = False

        self.message = None

    def executer(self):
        super().executer()
        self.action = "selection"
        self.menu_actuel = "principal"

        self.personnages = [instance_combat(personnage) for personnage in self.jeu.equipe.personnages]
        self.maj_tours()
        self.tour = self.tours.defiler()

    def maj_tours(self):
        combatants = self.personnages + self.ennemis

        combatants.sort(
            key=lambda x: (x["attributs"].get("vitesse", 0), x["type"] == "personnage"),
            # tri selon la vitesse, si égalité, on privilégie les personnages
            reverse=True
        )
        vitesse_moyenne = sum(combatant["attributs"].get("vitesse", 0) for combatant in combatants) / len(
            combatants) if combatants else 1

        for combatant in combatants:
            vitesse = combatant["attributs"].get("vitesse", 0)
            # permettre au combatant de jouer 2 fois si la vitesse est 2 fois supérieur à la moyenne
            nombre_tours = min(
                2,
                max(1, int(vitesse / vitesse_moyenne))  # minimum 1
            )
            for _ in range(nombre_tours):
                self.tours.enfiler(combatant)

    def set_message(self, message):
        self.message = (message, 90)

    def prochain_tour(self):
        if self.tours.est_vide():
            self.maj_tours()
        self.tour = self.tours.defiler()
        self.action = "pre-tour"
        self.menu_actuel = "principal"
        self.selection = 0
        self.debut_tour()

    def debut_tour(self):
        """
        Applique les effets sur le joueur/ennemi au début du tour.
        Gère la durée des effets.
        """
        perso = self.tour
        skip_tour = False

        effets = perso["effets"]
        for nom_effet, effet in effets:
            if nom_effet == "brulure":
                perso["attributs"]["vie"] -= effet[0]
            elif nom_effet == "regeneration":
                perso["attributs"]["vie"] += perso["attributs"]["vie_max"] * (
                            effet[0] * 5 / 100)  # soigner 5% de la vie max par niveau de regeneration
            elif nom_effet == "etourdissement":
                skip_tour = True
                del effets["etourdissement"]

            if effet[1] > 0:
                effets[nom_effet][1] -= 1

            if effets[nom_effet][1] == 0:
                del effets[nom_effet]

        if skip_tour:
            self.prochain_tour()
        else:
            self.action = "selection"

    def calcul_degats(self, attaquant, cible):
        arme = attaquant.get("arme")
        if arme is None:
            arme = {
                "degats": 1,
                "critique": 5
            }
        degats = arme.get("degats", 1) + attaquant["attributs"].get("force", 1)
        crit = arme.get("critique", 5) + attaquant["attributs"].get("chance", 1) > random.randint(1, 100)
        if crit:
            degats *= 2

        # marque
        if "marque" in cible["effets"]:
            degats *= 1.5
            del cible["effets"]["marque"]

        return degats

    def utiliser_competence(self, personnage, cibles=None):
        self.action = "attaque"
        self.jeu.equipe.get_personnage(personnage.nom).utiliser_competence(self, self.competence_en_cours, cibles)

    def changer_menu(self, menu):
        self.menu_actuel = menu
        self.selection = 0

    def update_ennemi(self, events):
        ennemi = self.tour

        if self.action == "selection":
            
            attaque = random.choice(ennemi["attaques"])
            self.attaques = [
                {**action, "focus": False, "processed": False}
                for action in attaque["actions"]
            ]
            self.action == "attaque"
            
        elif self.action == "attaque":
            
            for window in self.attaques:
                
                pass
            

    def update_selection(self, events):
        perso_actuel = self.tour
        ennemis_vivants = [index for index, ennemi in enumerate(self.ennemis) if ennemi["vie"] > 0]

        if self.menu_actuel == "principal":

            self.options = range(3 if "silence" not in perso_actuel["effets"] else 2)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.selection == 0:
                            self.changer_menu("attaque")
                        elif self.selection == 1:
                            self.changer_menu("items")
                        elif self.selection == 2:
                            self.changer_menu("competences")

        elif self.menu_actuel == "attaque":

            self.options = ennemis_vivants
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ennemi = self.ennemis[ennemis_vivants[self.selection]]
                        degats = self.calcul_degats(perso_actuel, ennemi)
                        ennemi["vie"] -= degats
                        perso_actuel["pa"] += 1
                        self.prochain_tour()
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "items":
            items_disponibles = [
                (id, qte) for id, qte in self.jeu.equipe.inventaire.items()
                if (item_data := self.jeu.loader.items.get(id)) and item_data.get("type", "") == "consommable"
            ]
            self.options = items_disponibles
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if len(items_disponibles) > 0:
                        if event.key == pygame.K_SPACE:
                            pass
                        elif event.key == pygame.K_ESCAPE:
                            self.changer_menu("principal")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "competences":
            competences = perso_actuel["competences"]
            self.options = competences
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        competence_selectionnee = competences[self.selection]
                        cible_type = competence_selectionnee.get("cible")
                        self.competence_en_cours = competence_selectionnee
                        if cible_type is None:
                            self.select_competence(competence_selectionnee)
                        elif cible_type == "ennemi":
                            self.changer_menu("cible_ennemi")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")
        elif self.menu_actuel == "cible_ennemi":
            self.options = ennemis_vivants
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        target_dict = self.ennemis[ennemis_vivants[self.selection]]
                        target_obj = self.jeu.equipe.get_personnage(target_dict["nom"])

                        self.select_competence(self.competence_en_cours["id"], target_dict)
                        attacker_obj = self.jeu.equipe.get_personnage(self.tour["nom"])
                        attacker_obj.target = target_obj
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("competences")

    def update_anim_personnages(self):
        for perso in self.personnages:
            perso_obj = self.jeu.equipe.get_personnage(perso["nom"])
            if perso_obj:
                perso_obj.update(
                    state=perso_obj.action,
                    a_distance=perso.get("a_distance", False),
                    target=perso_obj.target
                )

    def select_competence(self, competence_id, target=None):
        if self.action_en_cours:
            return
        self.jeu.equipe.get_personnage(self.tour["nom"]).utiliser_competence(competence_id, target)
        self.action_en_cours = True

    def on_hit(self, attacker, target):
        degats = self.calcul_degats(attacker, target)
        target["vie"] -= degats

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selection = (self.selection + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selection = (self.selection - 1) % len(self.options)
        if self.tour["type"] == "personnage":
            if self.action == "selection":
                self.update_selection(events)
            if self.action == "attaque":
                pass
        elif self.tour["type"] == "ennemi":
            self.update_ennemi(events)

        self.update_anim_personnages()

    # AFFICHAGE

    def draw_qte(self, current_frame, window_start, window_end, pos=(500, 300)):
        if not (window_start <= current_frame <= window_end):
            return

        pygame.draw.rect(self.jeu.ui_surface, (118, 129, 171), (pos[0] - 10, pos[1] - 10, 20, 20))

        # Calculer la progression de l'indicateur (0.0 à 1.0)
        total_frames = window_end - window_start
        progress = (current_frame - window_start) / total_frames if total_frames > 0 else 0
        progress = max(0, min(1, progress))  # Limiter entre 0 et 1

        # Périmètre total du carré (4 côtés de 20 pixels)
        indicator_pos = progress * (4 * 20)

        # Déterminer la position de l'indicateur sur le carré
        if indicator_pos < 20:  # cote haut (gauche -> droite)
            indicator_x = pos[0] - 10 + indicator_pos
            indicator_y = pos[1] - 10
        elif indicator_pos < 40:  # cote droit (haut -> bas)
            indicator_x = pos[0] + 10
            indicator_y = pos[1] - 10 + (indicator_pos - 20)
        elif indicator_pos < 60:  # cote bas (droite -> gauche)
            indicator_x = pos[0] + 10 - (indicator_pos - 40)
            indicator_y = pos[1] + 10
        else:  # cote gauche (bas -> haut)
            indicator_x = pos[0] - 10
            indicator_y = pos[1] + 10 - (indicator_pos - 60)

        # Dessiner l'indicateur
        pygame.draw.circle(self.jeu.ui_surface, (255, 255, 255), (int(indicator_x), int(indicator_y)), 3)

        pygame.draw.line(self.jeu.ui_surface, (245, 205, 0), (pos[0], pos[1]), (pos[0], pos[1] + 20), 2)

    def draw_selection(self, options):
        option_height = total_height / len(options)
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == self.selection else (200, 200, 200)
            if i == self.selection:
                pygame.draw.rect(
                    self.jeu.ui_surface,
                    couleur_hightlight,
                    (separator_x + 2, box_y + i * option_height, menu_width - 5, option_height)
                )

            text_render_centered_left(
                self.jeu.ui_surface,
                option,
                "bold" if i == self.selection else "regular",
                color,
                (separator_x + 20, box_y + i * option_height + option_height / 2),
                size=22
            )

    def draw_menu(self):

        pygame.draw.rect(
            self.jeu.ui_surface,
            (0, 0, 0),
            (box_x - 3, box_y - 3, box_width + 6, total_height + 6),
        )
        pygame.draw.line(
            self.jeu.ui_surface,
            (0, 0, 0, 150),
            (separator_x, box_y + 2),
            (separator_x, box_y + total_height - 4),
            2
        )

        text_render_centered_left(
            self.jeu.ui_surface,
            self.tour["nom"],
            "bold",
            (255, 255, 255),
            (box_x + 7, box_y + 20),
            size=26
        )

        # vie
        ratio_vie = self.tour["attributs"]['vie'] / self.tour["attributs"]['vie_max']
        text_render_centered_left(
            self.jeu.ui_surface,
            f"Vie : {self.tour['attributs']['vie']}/{self.tour['attributs']['vie_max']}",
            "imregular",
            (200, 200, 200),
            (box_x + 7, box_y + 50),
            size=18
        )

        # barre de vie
        bar_width = 180
        bar_height = 20
        pygame.draw.rect(
            self.jeu.ui_surface,
            (50, 50, 50),
            (box_x + 5, box_y + 63, bar_width + 4, bar_height + 4)
        )
        pygame.draw.rect(
            self.jeu.ui_surface,
            (255, 0, 0) if ratio_vie > 0.5 else (255, 165, 0) if ratio_vie > 0.25 else (139, 0, 0),
            (box_x + 7, box_y + 65, bar_width * ratio_vie, bar_height)
        )

        # pa
        max_pa = 8
        text_render_centered_left(
            self.jeu.ui_surface,
            f"PA : {self.tour['pa']}/{max_pa}",
            "imregular",
            (200, 200, 200),
            (box_x + 7, box_y + 110),
            size=18
        )

        pa_ratio = self.tour['pa'] / max_pa
        pygame.draw.rect(
            self.jeu.ui_surface,
            (50, 50, 50),
            (box_x + 5, box_y + 123, bar_width + 4, bar_height + 4)
        )
        pygame.draw.rect(
            self.jeu.ui_surface,
            (21, 169, 232),
            (box_x + 7, box_y + 125, bar_width * pa_ratio, bar_height)
        )
        for i in range(max_pa):
            ratio = i / max_pa * bar_width
            pygame.draw.line(
                self.jeu.ui_surface,
                (0, 0, 0),
                (box_x + 5 + ratio, box_y + 125),
                (box_x + 5 + ratio, box_y + 125 + bar_height),
            )
            
        if self.menu_actuel == "principal":
            
            options = ["Attaque", "Items", "Compétences"]
            if "silence" in self.tour["effets"]:
                options = ["Attaque", "Items"]
            self.draw_selection(options)
        
        elif self.menu_actuel == "attaque":
            
            ennemis_vivants = [ennemi for ennemi in self.ennemis if ennemi["vie"] > 0]
            self.draw_selection([ennemi["nom"] for ennemi in ennemis_vivants])
            
        elif self.menu_actuel == "items":
            
            items_disponibles = [
                (identifiant, qte) for identifiant, qte in self.jeu.equipe.inventaire.items()
                if
                (item_data := self.jeu.loader.items.get(identifiant)) and item_data.get("type", "") == "consommable"
            ]
            if not items_disponibles:
                text_render_centered_left(
                    self.jeu.ui_surface,
                    "Aucun objet utilisable",
                    "imitalic",
                    (150, 150, 150),
                    (separator_x + 20, box_y + 37),
                    size=18                    
                )
            else:
                option_height = total_height / len(items_disponibles)
                for i, (item_id, qte) in enumerate(items_disponibles):
                    item_data = self.jeu.loader.items.get(item_id)
                    color = (255, 255, 255) if i == self.selection else (200, 200, 200)
                    if i == self.selection:
                        pygame.draw.rect(
                            self.jeu.ui_surface,
                            couleur_hightlight,
                            (separator_x + 2, box_y + i * option_height, menu_width - 5, option_height)
                        )
                    text_render_centered_left(
                        self.jeu.ui_surface,
                        f"{item_data['nom']} x{qte}",
                        "bold" if i == self.selection else "regular",
                        color,
                        (separator_x + 20, box_y + i * option_height + option_height / 2),
                        size=18
                    )
                    
        elif self.menu_actuel == "competence":
            
            competences = self.tour["competences"]
            self.draw_selection([comp["nom"] for comp in competences])
            
        elif self.menu_actuel == "cible_ennemi":
            
            ennemis_vivants = [ennemi for ennemi in self.ennemis if ennemi["vie"] > 0]
            self.draw_selection([ennemi["nom"] for ennemi in ennemis_vivants])

    def draw_ui(self):
        # menu
        if self.action == "selection" and self.tour["type"] == "personnage":
            self.draw_menu()

    def draw(self):

        self.draw_ui()
        for perso in self.personnages:
            perso_obj = self.jeu.equipe.get_personnage(perso["nom"])
            if perso_obj:
                perso_obj.draw()

        if self.tour and self.tour.get("attacking", False):
            attacker = self.jeu.equipe.get_personnage(self.tour["nom"])
            target = self.tour.get("target")
            if attacker and target:
                target_obj = self.jeu.equipe.get_personnage(target)
                if target_obj:
                    original_pos = attacker.rect.copy()
                    if not self.tour.get("a_distance", False):
                        attacker.move(target_obj.rect.x - 50, target_obj.rect.y)
                    attacker.draw()
                    attacker.rect = original_pos
