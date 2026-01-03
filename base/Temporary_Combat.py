import pygame
import random
from lib.render import text_render_centered, text_render_centered_left
from .Action import Action
from lib.file import File

parrysound = pygame.mixer.Sound("assets/sounds/parry.mp3")
parrysound.set_volume(0.05)


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
            if id_competence in personnage.competences_debloques
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

        self.tours = File()
        self.tour = None
        self.action = None

        self.ennemis = [transformer_ennemi(ennemi) for ennemi in self.jeu.equipe.ennemis]
        self.personnages = []

        self.menu_actuel = "principal"
        self.selection = 0
        

    def executer(self):
        self.action = "selection"
        self.menu_actuel = "principal"

        self.personnages = [instance_combat(personnage) for personnage in self.jeu.equipe.personnages]
        self.maj_tours()

    def maj_tours(self):
        combatants = self.personnages + self.ennemis

        combatants.sort(
            key=lambda x: (x["attributs"].get("vitesse", 0), x["type"] == "personnage"),
            # tri selon la vitesse, si égalité, on privilégie les personnages
            reverse=True
        )
        vitesse_moyenne = sum(combatant["vitesse"] for combatant in combatants) / len(
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

    def prochain_tour(self):
        if self.tours.est_vide():
            self.maj_tours()
        self.tour = self.tours.defiler()
        self.action = "selection"
        self.menu_actuel = "principal"
        self.selection = 0

    def debut_tour(self):
        """
        Applique les effets sur le joueur au début du tour.
        Gère la durée des effets.
        """
        perso = self.tour

        effets = perso["effets"]
        for nom_effet, effet in effets:
            match nom_effet:
                case "brulure":
                    perso["attributs"]["vie"] -= effet[0]
                case "regeneration":
                    perso["attributs"]["vie"] += perso["attributs"]["vie_max"] * (
                            effet[0] * 5 / 100)  # soigner 5% de la vie max par niveau de regeneration
                case "etourdissement":
                    self.prochain_tour()
                    del effets[nom_effet]
                    continue  # finir l'itération pour éviter toute erreur puisque l'on retire l'effet

            if effet[1] > 0:
                effets[nom_effet][1] -= 1
            if effets[nom_effet][1] == 0:
                del effets[nom_effet]

    def calcul_degats(self, attaquant, cible):
        degats = attaquant["arme"].get("degats", 1) + attaquant["attributs"].get("force", 1)
        crit = attaquant["arme"].get("critique", 5) + attaquant["attributs"].get("chance", 1) > random.randint(1, 100)
        if crit:
            degats *= 2

        # marque
        if "marque" in cible["effets"]:
            degats *= 1.5
            del cible["effets"]["marque"]

        return degats

    def utiliser_competence(self, personnage, cible=None):
        self.action = "attaque"
        self.jeu.equipe.get_personnage(personnage.nom).utiliser_competence(self, self.competence_en_cours, cible)

    def changer_menu(self, menu):
        self.menu_actuel = menu
        self.selection = 0

    def update_tour_ennemi(self, events):
        pass

    def update_tour_joueur(self, events):
        perso_actuel = self.tour
        ennemis_vivants = [index for index, ennemi in enumerate(self.ennemis) if ennemi["vie"] > 0]

        if self.menu_actuel == "principal":
            for event in events:
                max_selection = 3 if "silence" not in perso_actuel["effets"] else 2
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % max_selection
                    elif event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % max_selection
                    elif event.key == pygame.K_SPACE:
                        match self.selection:
                            case 0:
                                self.changer_menu("attaque")
                            case 1:
                                self.changer_menu("items")
                            case 2:
                                self.changer_menu("competences")

        elif self.menu_actuel == "attaque":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % len(ennemis_vivants)
                    elif event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % len(ennemis_vivants)
                    elif event.key == pygame.K_SPACE:
                        ennemi = self.ennemis[ennemis_vivants[self.selection]]
                        degats = self.calcul_degats(perso_actuel, ennemi)
                        ennemi["vie"] -= degats
                        perso_actuel["pa"] += 1
                        self.prochain_tour()
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "items":
            items_disponibles = {
                identifiant: quantite for identifiant, quantite in self.jeu.equipe.inventaire.values()
                if (item_data := self.jeu.loader.items.get(id)) and item_data.get("type", "") == "consommable"
                #             ^ assigne et vérifie item_data
            }
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if len(items_disponibles) > 0:
                        if event.key == pygame.K_DOWN:
                            self.selection = (self.selection + 1) % len(items_disponibles)
                        elif event.key == pygame.K_UP:
                            self.selection = (self.selection - 1) % len(items_disponibles)
                        elif event.key == pygame.K_SPACE:
                            pass
                        elif event.key == pygame.K_ESCAPE:
                            self.changer_menu("principal")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "competences":
            competences = perso_actuel["competences"]
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % len(competences)
                    elif event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % len(competences)
                    elif event.key == pygame.K_SPACE:
                        competence_selectionnee = competences[self.selection]
                        cible_type = competence_selectionnee.get("cible")
                        self.competence_en_cours = competence_selectionnee
                        if cible_type is None:
                            pass
                        elif cible_type == "ennemi":
                            self.changer_menu("cible_ennemi")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "cible_ennemi":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selection = (self.selection + 1) % len(ennemis_vivants)
                    elif event.key == pygame.K_UP:
                        self.selection = (self.selection - 1) % len(ennemis_vivants)
                    elif event.key == pygame.K_SPACE:
                        pass
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("competences")

    def update(self, events):
        if self.tour["type"] == "ennemi":
            self.update_tour_ennemi(events)
        elif self.tour["type"] == "personnage" and self.action == "selection":
            self.update_tour_joueur(events)
        for perso_dict in self.personnages:
            perso_obj=self.jeu.equipe.get_personnage(perso_dict["nom"])
            if perso_obj:
                perso_obj.update(
                    state=perso_obj.action,
                    a_distance=perso_dict.get("a_distance", False),
                    target=perso_obj.target)
    def select_competence(self,competence_id,target=None):
        if self.action_en_cours:
            return
        self.jeu.equipe.get_personnage(self.tour.nom).play_competence(competence_id,target)
        self.action_en_cours=True
    def on_hit(self, attacker_obj, target_dict):
        degats = self.calcul_degats(
            self.tour,
            target_dict)
        target_dict["vie"] -= degats
    # AFFICHAGE

    def draw_qte(self, current_frame, window_start, window_end, pos=(500, 300)):
        if window_start <= current_frame <= window_end:
            pass

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

    def draw_menu(self):
        pass

    def draw_ui(self):
        pass

    def draw(self):
        
        self.draw_ui()
        for perso_dict in self.personnages:
            perso_obj=self.jeu.equipe.get_personnage(perso_dict["nom"])
            if perso_obj:
                perso_obj.draw(self.jeu.fond)
        if self.tour and self.tour.get("attacking",False):
            attacker_obj=self.jeu.equipe.get_personnage(self.tour["nom"])
            target_dict=self.tour.get("target")
            if attacker_obj and target_dict:
                target_obj=self.jeu.equipe.get_personnage(target_dict['nom'])
                if target_obj:
                    original_pos=attacker_obj.rect.copy()
                    if not self.tour.get("a_distance",False):
                        attacker_obj.move(target_obj.rect.x-50,target_obj.rect.y)
                    attacker_obj.draw(self.jeu.fond)
                    attacker_obj.rect=original_pos
