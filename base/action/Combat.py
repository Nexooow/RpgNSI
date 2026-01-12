import pygame
import random

from lib.combat import add_effets, calcul_degats
from lib.render import text_render_centered_left, text_render_centered
from .Action import Action
from lib.file import File
from lib.sounds import son_selection

parrysound = pygame.mixer.Sound("assets/sounds/parry.mp3")
parrysound.set_volume(0.05)

total_height = 200
box_y = 700 - total_height - 20
box_width = 960
box_x = 20
couleur_hightlight = (70, 70, 90)

separator_x = box_x + 400

menu_width = box_width - (separator_x - box_x)
max_pa = 8


def instance_combat(personnage):
    """
    Convertit le personnage en instance utilisable pour le combat (ajout d'attributs nécessaires; effets ...)
    """
    return {
        "type": "personnage",
        **personnage.__dict__,
        "effets": {},  # cle: nom de l'effet, valeur : (niveau, durée)
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
        "vie_depart": ennemi["vie"],
        **ennemi,
        "effets": {}
    }
    if 'image' in ennemi:
        instance["image_surface"]=pygame.transform.scale(pygame.image.load(ennemi['image']),(120,120))
    if "attributs" not in ennemi:
        instance["attributs"] = {}
    instance["attributs"]["vie"] = instance["vie_depart"]
    return instance


def ajouter_pa(combatant):
    if combatant["pa"] < max_pa:
        combatant["pa"] += 1


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
        self.sub_frame_count = 0

        self.menu_actuel = "principal"
        self.selection = 0
        self.item_en_cours = None

        self.message = None
        self.image = pygame.transform.scale(pygame.image.load("./assets/sprites/fight_zone_generic.jpg"), (1000, 700)).convert()
        

    def executer(self):
        super().executer()
        self.action = "selection"
        self.menu_actuel = "principal"
        self.jeu.jouer_musique(self.musique, loop=True, volume=0.2)

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
            if combatant["attributs"].get("vie", 0) <= 0:
                continue

            vitesse = combatant["attributs"].get("vitesse", 0)
            # permettre au combatant de jouer 2 fois si la vitesse est 2 fois supérieur à la moyenne
            nombre_tours = min(
                2,
                max(1, int(vitesse / vitesse_moyenne))  # minimum 1
            )

            instance_index = self.personnages.index(combatant) \
                if combatant["type"] == "personnage" \
                else self.ennemis.index(combatant)

            for _ in range(nombre_tours):
                self.tours.enfiler([combatant["type"], instance_index])

    def get_perso_tour(self):
        tour = self.tour
        if tour[0] == "personnage":
            return self.personnages[tour[1]]
        elif tour[0] == "ennemi":
            return self.ennemis[tour[1]]

    def set_message(self, message):
        self.message = (message, 200)

    def prochain_tour(self):
        if self.tours.est_vide():
            self.maj_tours()
        self.tour = self.tours.defiler()
        self.action = "pre-tour"
        self.menu_actuel = "principal"
        self.selection = 0
        self.debut_tour()

    def synchroniser_stats_equipe(self):
        """
        Synchronise les stats des personnages du combat avec ceux de l'équipe.
        Appelé à la fin du combat.
        """
        for perso_combat in self.personnages:
            perso_equipe = self.jeu.equipe.get_personnage(perso_combat["nom"])
            if perso_equipe:
                perso_equipe.attributs["vie"] = perso_combat["attributs"]["vie"]
                perso_equipe.alive = perso_combat["attributs"]["vie"] > 0

    def debut_tour(self):
        """
        Applique les effets sur le joueur/ennemi au début du tour.
        Gère la durée des effets.
        """
        perso = self.get_perso_tour()
        skip_tour = False

        effets = perso["effets"]
        effets_a_supprime = []
        for nom_effet, (niveau, duree) in effets.items():
            if nom_effet == "brulure":
                perso["attributs"]["vie"] -= niveau
            elif nom_effet == "regeneration":
                perso["attributs"]["vie"] += perso["attributs"]["vie_max"] * (
                        niveau * 5 / 100)  # soigner 5% de la vie max par niveau de regeneration
            elif nom_effet == "etourdissement":
                skip_tour = True
                effets_a_supprime.append("etourdissement")

            if duree > 0:
                effets[nom_effet][1] -= 1

            if effets[nom_effet][1] == 0:
                effets_a_supprime.append(nom_effet)

        for nom_effet in effets_a_supprime:
            del effets[nom_effet]

        if skip_tour or perso["attributs"].get("vie", 0) <= 0:
            self.prochain_tour()
        else:
            self.action = "selection"

    def utiliser_competence(self, personnage, cibles=None):
        self.action = "attaque"
        self.jeu.equipe.get_personnage(personnage.nom).utiliser_competence(self, self.competence_en_cours, personnage,
                                                                           cibles)

    def changer_menu(self, menu):
        self.menu_actuel = menu
        self.selection = 0

    def update_ennemi(self, events):
        ennemi = self.get_perso_tour()

        if self.action == "selection":

            attaque = random.choice(ennemi["attaques"])
            cible = random.choice(
                [perso for perso in self.personnages if perso["attributs"]["vie"] > 0]
            )

            # Afficher le message d'attaque
            nom_attaque = attaque.get("nom", "Attaque")
            self.set_message(f"{ennemi['nom']} utilise {nom_attaque} sur {cible['nom']}")

            # Créer les attaques avec positions
            actions_avec_positions = []
            parry_count = 0
            for action in attaque["actions"]:
                action_dict = {
                    **action,
                    "cible": self.personnages.index(cible) if "cible" not in action else None,
                    "focus": False,
                    "processed": False
                }

                # Ajouter les positions x, y
                if action.get("type") == "parry":
                    # Utiliser la position prédéfinie si elle existe, sinon la calculer
                    if "pos_x" not in action or "pos_y" not in action:
                        action_dict["pos_x"] = 500 + (parry_count % 2) * 150 - 75
                        action_dict["pos_y"] = 350 + (parry_count // 2) * 150 - 75
                    else:
                        action_dict["pos_x"] = action["pos_x"]
                        action_dict["pos_y"] = action["pos_y"]
                    parry_count += 1
                else:
                    # Positions par défaut pour les autres types d'attaques
                    action_dict["pos_x"] = action.get("pos_x", 500)
                    action_dict["pos_y"] = action.get("pos_y", 350)

                actions_avec_positions.append(action_dict)

            self.attaques = actions_avec_positions
            self.sub_frame_count = 0
            self.action = "attaque"

        elif self.action == "attaque":

            all_processed = True
            found_focused = False

            for attaque in self.attaques:

                if attaque["processed"]:
                    continue
                all_processed = False

                cible = self.personnages[attaque["cible"]]

                if attaque["w_end"] == self.sub_frame_count:
                    attaque["processed"] = True
                    if cible:
                        if "damage" in attaque:
                            cible["attributs"]["vie"] -= attaque["damage"]
                        add_effets(cible, attaque.get("effets", {}))
                    continue

                if attaque["w_start"] <= self.sub_frame_count:
                    if not attaque["focus"] and not found_focused:
                        attaque["focus"] = True
                        found_focused = True
                    for event in events:
                        if event.type == pygame.KEYDOWN and (event.key == pygame.K_e or event.key == pygame.K_SPACE):
                            if attaque.get("type") == "parry" and attaque["focus"] == True:
                                # Vérifier si l'indicateur est dans la zone dorée
                                if self.est_timing_parry(attaque):
                                    # Parry réussi
                                    parrysound.play()
                                    ajouter_pa(cible)
                                    attaque["processed"] = True
                                else:
                                    # Parry échoué
                                    if "damage" in attaque:
                                        cible["attributs"]["vie"] -= attaque["damage"]
                                    add_effets(cible, attaque.get("effets", {}))
                                    attaque["processed"] = True

            if all_processed:
                self.prochain_tour()

    def update_selection(self, events):
        perso_actuel = self.get_perso_tour()
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
                        degats = calcul_degats(perso_actuel, ennemi)
                        ennemi["attributs"]["vie"] -= degats
                        ajouter_pa(perso_actuel)
                        self.set_message(f"{perso_actuel['nom']} attaque {ennemi['nom']} (-{int(degats)} PV)")
                        self.prochain_tour()
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "items":

            items_disponibles = [
                (identifiant, qte) for identifiant, qte in self.jeu.equipe.inventaire.items()
                if (item_data := self.jeu.loader.items.get(identifiant)) and item_data.get("type", "") == "consommable"
            ]
            self.options = items_disponibles
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if len(items_disponibles) > 0:
                        if event.key == pygame.K_SPACE:
                            item_id, _ = items_disponibles[self.selection]
                            self.item_en_cours = item_id
                            item_data = self.jeu.loader.items.get(item_id)
                            cible_type = item_data.get("cible", "soi")
                            if cible_type == "soi":
                                self.utiliser_item(item_id, perso_actuel)
                            elif cible_type == "allie":
                                self.changer_menu("cible_allie_item")
                            elif cible_type == "ennemi":
                                self.changer_menu("cible_ennemi_item")
                            else:
                                # Par défaut, utiliser sur soi-même
                                self.utiliser_item(item_id, perso_actuel)
                        elif event.key == pygame.K_ESCAPE:
                            self.changer_menu("principal")
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("principal")

        elif self.menu_actuel == "cible_allie_item":

            allies_vivants = [index for index, perso in enumerate(self.personnages) if perso["attributs"]["vie"] > 0]
            self.options = allies_vivants
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        cible = self.personnages[allies_vivants[self.selection]]
                        self.utiliser_item(self.item_en_cours, cible)
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("items")

        elif self.menu_actuel == "cible_ennemi_item":

            self.options = ennemis_vivants
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        cible = self.ennemis[ennemis_vivants[self.selection]]
                        self.utiliser_item(self.item_en_cours, cible)
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("items")

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
                            self.select_competence(competence_selectionnee["id"])
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
                        competence_id = self.competence_en_cours["id"]
                        self.select_competence(competence_id, target_dict)
                    elif event.key == pygame.K_ESCAPE:
                        self.changer_menu("competences")

    def update_anim_personnages(self):
        for perso in self.personnages:
            perso_obj = self.jeu.equipe.get_personnage(perso["nom"])
            if perso_obj:
                perso_obj.update(
                    state=perso_obj.action,
                    # a_distance=perso.get("a_distance", False),
                    # target=perso_obj.target
                )

    def select_competence(self, competence_id, target=None):
        perso_dict = self.get_perso_tour()
        if target is None:
            target = [self.personnages, self.ennemis]
        classe_personnage = self.jeu.equipe.get_personnage(perso_dict["nom"])
        competence = classe_personnage.competences[competence_id]
        if competence["cost"]["pa"] > perso_dict["pa"]:
            self.set_message("PA insuffisants !")
            return
        if "mitigation" in competence["cost"]:
            niveau_effet = perso_dict["effets"].get("mitigation", (0, 0))[0]
            if niveau_effet < competence["cost"]["mitigation"]:
                self.set_message("Effet 'mitigation' requis !")
                return
            else:
                perso_dict["effets"]["mitigation"][1] -= 1
                if perso_dict["effets"]["mitigation"][1] <= 0:
                    del perso_dict["effets"]["mitigation"]
        if "elan" in competence["cost"]:
            niveau_effet = perso_dict["effets"].get("elan", (0, 0))[0]
            if niveau_effet < competence["cost"]["elan"]:
                self.set_message("Effet 'élan' requis !")
                return
            else:
                perso_dict["effets"]["elan"][1] -= 1
                if perso_dict["effets"]["elan"][1] <= 0:
                    del perso_dict["effets"]["elan"]

        # Afficher le message de compétence
        if isinstance(target, dict):
            self.set_message(f"{perso_dict['nom']} utilise {competence['nom']} sur {target['nom']}")
        else:
            self.set_message(f"{perso_dict['nom']} utilise {competence['nom']}")

        classe_personnage.utiliser_competence(competence_id, perso_dict, target)
        perso_dict["pa"] -= classe_personnage.competences[competence_id]["cost"]["pa"]
        print(classe_personnage.competences[competence_id]["cost"]["pa"], perso_dict["pa"])
        self.prochain_tour()

    def utiliser_item(self, item_id, cible):
        """
        Utilise un item consommable sur une cible.
        Gère les différents effets: heal, buffs, debuffs, etc.
        """
        item_data = self.jeu.loader.items.get(item_id)
        if not item_data:
            return

        effets = item_data.get("effets", {})

        for nom_effet, (niveau, duree) in effets.items():
            if nom_effet == "heal":
                # Soigner la cible
                vie_max = cible["attributs"].get("vie_max", cible.get("vie_depart", 100))
                cible["attributs"]["vie"] = min(
                    cible["attributs"]["vie"] + niveau,
                    vie_max
                )
            elif nom_effet == "restore_pa":
                # Restaurer des PA
                cible["pa"] = min(cible["pa"] + niveau, max_pa)
            elif nom_effet == "damage":
                # Infliger des dégâts directs
                cible["attributs"]["vie"] -= niveau
            else:
                # Autres effets (buffs/debuffs) - utiliser add_effets
                add_effets(cible, {nom_effet: [niveau, duree]})

        # Retirer l'item de l'inventaire
        if item_id in self.jeu.equipe.inventaire:
            self.jeu.equipe.inventaire[item_id] -= 1
            if self.jeu.equipe.inventaire[item_id] <= 0:
                del self.jeu.equipe.inventaire[item_id]

        # Afficher un message
        self.set_message(f"{cible['nom']} utilise {item_data['nom']}")

        # Passer au tour suivant
        self.prochain_tour()

    def on_hit(self, attacker, target):
        degats = calcul_degats(attacker, target)
        target["attributs"]["vie"] -= degats

    def update(self, events):

        self.sub_frame_count += 1

        # Gestion du message
        if self.message is not None:
            texte, duree = self.message
            if duree > 0:
                self.message = (texte, duree - 1)
            else:
                self.message = None

        ennemi_vivants = False
        for ennemi in self.ennemis:
            if ennemi["attributs"]["vie"] > 0:
                ennemi_vivants = True
                break

        personnages_vivants = False
        for perso in self.personnages:
            if perso["attributs"]["vie"] > 0:
                personnages_vivants = True
                break

        if not personnages_vivants or not ennemi_vivants:
            # Synchroniser les stats des personnages avec l'équipe
            self.synchroniser_stats_equipe()

            if not personnages_vivants:
                # Tous les personnages sont morts → téléporter à l'auberge et soigner
                self.jeu.region = "Auberge"
                self.jeu.lieu = self.jeu.regions["Auberge"].entree
                self.jeu.equipe.soigner_complet()
                self.jeu.actions.contenu = []
                self.set_message("L'équipe a été vaincue... Retour à l'auberge.")

            self.complete = True

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    son_selection.play()
                    self.selection = (self.selection + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    son_selection.play()
                    self.selection = (self.selection - 1) % len(self.options)
        if self.tour[0] == "personnage":
            if self.action == "selection":
                self.update_selection(events)
            if self.action == "attaque":
                pass
        elif self.tour[0] == "ennemi":
            self.update_ennemi(events)

        self.update_anim_personnages()

    # AFFICHAGE

    def est_timing_parry(self, window):
        """
        Vérifie si le timing pour parer est bon.
        L'attaque doit avoir des positions x, y définies (soit prédéfinies, soit auto-générées).
        """
        window_end = window["w_end"]
        window_start = window["w_start"]
        current_frame = self.sub_frame_count

        total_frames = window_end - window_start
        if total_frames <= 0:
            return False

        # Calculer la progression de l'indicateur (0.0 à 1.0)
        progress = (current_frame - window_start) / total_frames
        progress = max(0, min(1, progress))  # Limiter entre 0 et 1

        # Périmètre total du carré (4 côtés de 50 pixels)
        indicator_pos = progress * (4 * 50)

        # La zone dorée est le côté gauche (de 150 à 200 du périmètre)
        return 150 <= indicator_pos <= 200

    def draw_qte(self, window):
        # Utiliser la position prédéfinie dans l'attaque, ou utiliser une position par défaut
        pos = [window.get("pos_x", 500), window.get("pos_y", 350)]
        is_focused = window.get("focus", False)
        window_end = window["w_end"]
        window_start = window["w_start"]
        current_frame = self.sub_frame_count

        total_frames = window_end - window_start

        # Calculer la progression de l'indicateur (0.0 à 1.0)
        progress = (current_frame - window_start) / total_frames if total_frames > 0 else 0
        progress = max(0, min(1, progress))  # Limiter entre 0 et 1

        if progress == 0 or window["processed"]:
            return

        # Périmètre total du carré (4 côtés de 50 pixels)
        indicator_pos = progress * (4 * 50)

        # Déterminer la position de l'indicateur sur le carré
        if indicator_pos < 50:  # cote haut (gauche -> droite)
            indicator_x = pos[0] - 25 + indicator_pos
            indicator_y = pos[1] - 25
        elif indicator_pos < 100:  # cote droit (haut -> bas)
            indicator_x = pos[0] + 25
            indicator_y = pos[1] - 25 + (indicator_pos - 50)
        elif indicator_pos < 150:  # cote bas (droite -> gauche)
            indicator_x = pos[0] + 25 - (indicator_pos - 100)
            indicator_y = pos[1] + 25
        else:  # cote gauche (bas -> haut)
            indicator_x = pos[0] - 25
            indicator_y = pos[1] + 25 - (indicator_pos - 150)

        color = (0, 0, 0) if is_focused else (150, 150, 150)

        # Dessiner le carré principal
        pygame.draw.rect(self.jeu.ui_surface, color, (pos[0] - 25, pos[1] - 25, 50, 50))

        pygame.draw.line(self.jeu.ui_surface, (245, 205, 0), (pos[0] - 25, pos[1] - 25), (pos[0] - 25, pos[1] + 25), 3)

        # Dessiner l'indicateur
        pygame.draw.circle(self.jeu.ui_surface, (245, 205, 0), (int(indicator_x), int(indicator_y)),
                           3)

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

        perso_tour = self.get_perso_tour()

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
            perso_tour["nom"],
            "bold",
            (255, 255, 255),
            (box_x + 7, box_y + 20),
            size=26
        )

        # vie
        ratio_vie = perso_tour["attributs"]['vie'] / perso_tour["attributs"]['vie_max']
        text_render_centered_left(
            self.jeu.ui_surface,
            f"Vie : {perso_tour['attributs']['vie']}/{perso_tour['attributs']['vie_max']}",
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
        text_render_centered_left(
            self.jeu.ui_surface,
            f"PA : {perso_tour['pa']}/{max_pa}",
            "imregular",
            (200, 200, 200),
            (box_x + 7, box_y + 110),
            size=18
        )

        pa_ratio = perso_tour['pa'] / max_pa
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
            if "silence" in perso_tour["effets"]:
                options = ["Attaque", "Items"]
            self.draw_selection(options)

        elif self.menu_actuel == "attaque":

            ennemis_vivants = [ennemi for ennemi in self.ennemis if ennemi["attributs"]["vie"] > 0]
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

        elif self.menu_actuel == "competences":

            competences = perso_tour["competences"]
            self.draw_selection([comp["nom"] for comp in competences])

        elif self.menu_actuel == "cible_ennemi":

            ennemis_vivants = [ennemi for ennemi in self.ennemis if ennemi["attributs"]["vie"] > 0]
            self.draw_selection([ennemi["nom"] for ennemi in ennemis_vivants])

        elif self.menu_actuel == "cible_allie_item":

            allies_vivants = [perso for perso in self.personnages if perso["attributs"]["vie"] > 0]
            self.draw_selection([perso["nom"] for perso in allies_vivants])

        elif self.menu_actuel == "cible_ennemi_item":

            ennemis_vivants = [ennemi for ennemi in self.ennemis if ennemi["attributs"]["vie"] > 0]
            self.draw_selection([ennemi["nom"] for ennemi in ennemis_vivants])

    def draw_health_bar(self, x, y, vie, vie_max, width=100, height=8):
        """Dessine une barre de vie à la position donnée"""
        ratio_vie = max(0, vie / vie_max) if vie_max > 0 else 0

        # Fond noir
        pygame.draw.rect(self.jeu.ui_surface, (0, 0, 0), (x - width // 2, y, width + 2, height + 2))

        # Barre de vie (couleur dégradée selon la santé)
        if ratio_vie > 0.5:
            color = (0, 255, 0)  # Vert
        elif ratio_vie > 0.25:
            color = (255, 165, 0)  # Orange
        else:
            color = (255, 0, 0)  # Rouge

        pygame.draw.rect(self.jeu.ui_surface, color, (x - width // 2 + 1, y + 1, width * ratio_vie, height))

    def draw_ui(self):
        
        # Affichage du message
        if self.message is not None:
            texte, duree = self.message
            # Calcul de l'opacité pour un effet de fade-out
            alpha = min(255, duree * 3)
            text_render_centered(
                self.jeu.ui_surface,
                texte,
                "imregular",
                (255, 255, 255, alpha),
                (500, 80),
                size=24
            )

        # menu
        if self.action == "selection" and self.tour[0] == "personnage":
            self.draw_menu()
        elif self.action == "attaque" and self.tour[0] == "ennemi":
            for attaque in self.attaques:
                if attaque.get("type") == "parry":
                    self.draw_qte(attaque)

    def draw(self):
        self.jeu.ui_surface.blit(self.image, (0, 0))
        self.draw_ui()

        # Dessiner les personnages et leurs barres de vie
        for perso in self.personnages:
            perso_obj = self.jeu.equipe.get_personnage(perso["nom"])
            if perso_obj:
                perso_obj.draw()
                # Dessiner la barre de vie sous le personnage
                vie = perso["attributs"]["vie"]
                vie_max = perso["attributs"]["vie_max"]
                # Position sous le personnage
                bar_x = perso_obj.rect.centerx
                bar_y = perso_obj.rect.bottom + 5
                self.draw_health_bar(bar_x, bar_y, vie, vie_max, width=80, height=6)

        # Dessiner les ennemis et leurs barres de vie
        for ennemi in self.ennemis:
            # Calculer la barre de vie de l'ennemi
            vie = ennemi["attributs"]["vie"]
            vie_depart = ennemi["vie_depart"]
            

            # Chercher l'objet ennemi pour obtenir sa position
            # Les ennemis sont généralement affichés en haut de l'écran
            # On peut utiliser leur index pour positionner les barres
            ennemi_index = self.ennemis.index(ennemi)
            bar_x = 500 + ennemi_index * 200  # Position horizontale
            bar_y = 50 + ennemi_index * 30  # Position verticale
            if "image_surface" in ennemi:
                image = ennemi["image_surface"]
                self.jeu.ui_surface.blit(image, (bar_x - 60, bar_y +10))

            self.draw_health_bar(bar_x, bar_y, vie, vie_depart, width=120, height=8)

        perso_tour = self.get_perso_tour()
        if perso_tour and perso_tour.get("attacking", False):
            attacker = self.jeu.equipe.get_personnage(perso_tour["nom"])
            target = perso_tour.get("target")
            if attacker and target:
                target_obj = self.jeu.equipe.get_personnage(target)
                if target_obj:
                    original_pos = attacker.rect.copy()
                    if not perso_tour.get("a_distance", False):
                        attacker.move(target_obj.rect.x - 50, target_obj.rect.y)
                    attacker.draw()
                    attacker.rect = original_pos