import json
import pygame
import typing

from base.Personnage import Vous, Barman, Fachan
from base.action import Action, Deplacement, AjoutTemps, SelectionAction
from base.Loader import Loader
from base.Equipe import Equipe

from lib.config import sommets, aretes, positions_sommets, musiques_regions, fonds_regions
from lib.file import File
from lib.graph import Graph
from lib.render import text_render_centered

from menu.accueil import Accueil


class Jeu:
    WIDTH = 1000
    HEIGHT = 700

    def __init__(self):
        """
        Initialise le jeu, les variables globales et charge les ressources nécessaires via Loader.
        """

        self.identifiant = None
        self.running = True
        self.debute = False  # si le jeu a débuté ou non

        self.clock = pygame.time.Clock()
        self.fond = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.filter_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.musique_actuelle = None

        self.menu = Accueil(self)
        self.loader = Loader(self)
        
        # carte et regions/lieux
        self.carte = Graph(sommets, aretes, True, positions_sommets)
        self.equipe = Equipe(self)
        self.variables_jeu = {}  # variables utilisés par certaines actions (exemple : stock des boutiques ...)
        self.variables_jeu["jeu_termine"]=False
        self.variables_jeu["radahn_killed"]=False
        self.variables_jeu["demiurge_killed"]=False
        self.regions = self.loader.charger_regions()
        self.region = "Auberge"
        self.lieu = self.regions["Auberge"].entree
        self.temps = 24 + 12

        self.action_actuelle: typing.Optional[Action] = None
        self.actions = File()

        # filtres pour affichage
        self.fade = 300

        self.loader.charger()

    # GETTERS

    def get_temps(self):
        """
        Renvoie le temps actuel sous forme de tuple (jour, heure)
        """

        return divmod(self.temps, 24)  # retourne (temps//24, temps%24) donc (jour, heure)

    def get_region_actuelle(self):
        """
        Renvoie la région actuelle du jeu
        """

        if self.region is None:
            return None
        return self.regions[self.region]

    # GESTION PARTIES

    def demarrer(self, identifiant, save_json=None):
        """
        Demarre la partie avec l'identifiant donné, ou restaure une partie si un JSON de sauvegarde est fourni.
        :param identifiant: L'identifiant de la partie
        :param save_json: Le JSON de sauvegarde (optionnel)
        :return: None
        """

        self.debute = True
        self.menu = None
        self.identifiant = identifiant
        print(f"Démarrage de la partie avec l'identifiant {self.identifiant}")
        if save_json is not None:
            self.restaurer(save_json)
        else:
            self.equipe.ajouter_personnage(Vous(self.equipe))
        # self.executer_sequence("test_combat")

    def restaurer(self, save_json):
        """
        Restaure l'état du jeu à partir d'un JSON de sauvegarde.
        """

        self.region = save_json["region"]
        self.lieu = save_json["lieu"]
        self.temps = save_json["temps"]
        self.equipe.restaurer(save_json["equipe"])
        self.variables_jeu = save_json["variables_jeu"]
        if save_json["actions"]:
            for action in save_json["actions"]:
                action_instance = self.loader.creer_action(action)
                self.ajouter_action(action_instance)
        if save_json["action_actuelle"]:
            self.action_actuelle = self.loader.creer_action(save_json["action_actuelle"])
            self.action_actuelle.executer()

    def sauvegarder(self):
        """
        Sauvegarde l'état actuel du jeu dans un fichier JSON.
        """

        actions = [action.data for action in self.actions.contenu]
        data = {
            "id": self.identifiant,
            "equipe": self.equipe.sauvegarder(),
            "temps": self.temps,
            "region": self.region,
            "lieu": self.lieu,
            "variables_jeu": self.variables_jeu,
            "actions": actions,
            "action_actuelle": self.action_actuelle.data if self.action_actuelle else None
        }
        json.dump(data, open(f"./.data/saves/{self.identifiant}.json", "w"))

    def quitter(self):
        """
        Quitte le jeu proprement.
        """

        self.running = False

    # AFFICHAGE, ÉVÉNEMENTS ET GESTION DES ACTIONS

    def gerer_evenement(self, evenements):
        """
        Délègue la gestion des événements au menu ou à l'action actuelle.
        :param evenements: Liste des événements pygame
        :return: None
        """

        if self.menu is not None:
            self.menu.update(evenements)
        elif self.action_actuelle is not None:
            self.action_actuelle.update(evenements)

    def action_suivante(self):
        """
        Passe à l'action suivante dans la file d'actions et l'exécute.
        """

        self.action_actuelle = self.actions.defiler()
        self.action_actuelle.executer()

    def executer(self):
        """
        Gère l'exécution des actions dans la file d'actions.
        """

        if self.action_actuelle is None:
            if not self.actions.est_vide():
                self.action_suivante()
            elif self.debute:
                self.action_actuelle = SelectionAction(self, {"type": "selection-action"})
                self.action_actuelle.executer()
        else:
            if self.action_actuelle.get_complete():
                if not self.actions.est_vide():
                    self.action_suivante()
                else:
                    self.action_actuelle = None

        if self.action_actuelle is not None and not self.action_actuelle.utilise_musique:
            region_actuelle = self.get_region_actuelle()
            if region_actuelle is not None:
                musique_region = musiques_regions.get(region_actuelle.nom, None)
                self.jouer_musique(musique_region, loop=True, volume=0.07)
            else:
                self.jouer_musique(None)
        if self.variables_jeu.get("jeu_termine",False):
            self.ouvrir_menu(Accueil(self))
            self.debute=False
            self.action_actuelle=None
            self.actions=File()

    def scene(self):
        """
        Gère le dessin de la scène, que ce soit le menu ou l'action actuelle.
        """

        if self.menu is not None:
            self.menu.draw()
        elif self.debute:
            self.fond.fill((255, 255, 255))
            self.fond.blit(fonds_regions[self.region], (0, 0))
            if self.action_actuelle is not None:
                self.action_actuelle.draw()
            self.ui()
        self.filters()  # applique les filtres sur l'écran

    def ui(self):
        """
        Dessine l'interface utilisateur (UI) sur l'écran.
        """

        if not self.action_actuelle or (
                self.action_actuelle and not self.action_actuelle.desactive_ui
        ):
            (jour, heure) = self.get_temps()

            # dimensions boite temps
            box_width = 220
            box_height = 50
            box_x = 15
            box_y = 15

            # bordure
            pygame.draw.rect(
                self.fond,
                (40, 40, 50),
                (box_x - 2, box_y - 2, box_width + 4, box_height + 4),
            )
            pygame.draw.rect(
                self.fond, (25, 25, 35), (box_x, box_y, box_width, box_height)
            )

            # séparateur
            center_x = box_x + box_width // 2
            pygame.draw.line(
                self.fond,
                (100, 100, 120),
                (center_x, box_y + 8),
                (center_x, box_y + box_height - 8),
                1,
            )

            text_render_centered(
                self.ui_surface,
                f"Jour {jour}",
                "imregular",
                color=(200, 200, 255),
                pos=(box_x + box_width // 4, box_y + box_height // 2),
                size=22,
            )

            heure_format = f"{heure:02d}:00"
            text_render_centered(
                self.ui_surface,
                heure_format,
                "imregular",
                color=(255, 255, 200),
                pos=(box_x + 3 * box_width // 4, box_y + box_height // 2),
                size=22,
            )

            # boite région/lieu et argent
            info_box_width = 240
            info_box_height = 75
            info_box_x = self.WIDTH - info_box_width - 15
            info_box_y = 15

            # bordure
            pygame.draw.rect(
                self.fond,
                (40, 40, 50),
                (info_box_x - 2, info_box_y - 2, info_box_width + 4, info_box_height + 4),
            )
            pygame.draw.rect(
                self.fond, (25, 25, 35), (info_box_x, info_box_y, info_box_width, info_box_height)
            )

            # région et lieu
            region_lieu_text = f"{self.region}"
            if self.lieu:
                region_lieu_text += f" - {self.lieu}"
            text_render_centered(
                self.ui_surface,
                region_lieu_text,
                "imregular",
                color=(200, 255, 200),
                pos=(info_box_x + info_box_width // 2, info_box_y + 20),
                size=18,
            )

            # séparateur horizontal
            pygame.draw.line(
                self.fond,
                (100, 100, 120),
                (info_box_x + 8, info_box_y + info_box_height // 2),
                (info_box_x + info_box_width - 8, info_box_y + info_box_height // 2),
                1,
            )

            # argent de l'équipe
            argent_text = f"{self.equipe.argent} €"
            text_render_centered(
                self.ui_surface,
                argent_text,
                "imregular",
                color=(255, 215, 100),
                pos=(info_box_x + info_box_width // 2, info_box_y + info_box_height - 20),
                size=20,
            )

    def filters(self):
        """
        Applique les filtres d'écran (ex: fondu) sur l'écran de jeu.
        """

        if self.fade > 0:
            if self.fade < 8:
                self.fade = 2
            pygame.draw.rect(
                self.filter_surface,
                (0, 0, 0, min([self.fade, 255])),
                self.filter_surface.get_rect(),
            )
            self.fade -= 2

    def jouer_musique(self, musique, loop=True, volume=0.25):
        """
        Démarre une musique en boucle si elle n'est pas déjà en cours de lecture (pour éviter les coupures)
        :param musique: Le nom du fichier musique, rien pour arrêter la musique
        :param loop: Booléen, si la musique doit être en boucle ou non
        :param volume: Volume de la musique (0.0 à 1.0)
        """

        if musique is None or musique == "":
            pygame.mixer.music.stop()
            return
        if self.musique_actuelle != musique:
            pygame.mixer.music.load(f"./assets/music/{musique}.mp3")
            pygame.mixer.music.play(-1 if loop else 0)
            pygame.mixer.music.set_volume(volume)
            self.musique_actuelle = musique

    # GESTION ACTIONS

    def interagir(self, npc=None):
        """
        Gère l'interaction avec un PNJ donné ou avec le lieu actuel si aucun PNJ n'est spécifié.
        :param npc: L'identifiant du PNJ avec lequel interagir (optionnel)
        :return: None
        """

        if npc is None:
            npc = self.lieu
        if f"{npc}:rencontre" not in self.variables_jeu and self.loader.get_sequence(f"{npc}:rencontre"):
            self.executer_sequence(npc + ":rencontre")
            self.variables_jeu[f"{npc}:rencontre"] = True
        else:
            self.executer_sequence(npc + ":interaction")

    def ajouter_action(self, action):
        """
        Ajoute une action à la file d'actions.
        :param action: L'action à ajouter
        :return: None
        """
        print(action)
        assert isinstance(action,
                          Action), f"L'action à ajouter n'est pas une instance de la classe Action mais est de type {type(action)}"
        self.actions.enfiler(action)

    def executer_sequence(self, identifiant, priority=False):
        """
        Exécute une séquence d'actions identifiée par son identifiant.
        :param identifiant: L'identifiant de la séquence à exécuter
        :param priority: Si True, insère la séquence au début de la file d'actions
        :return: None
        """

        sequence = self.loader.get_sequence(identifiant)
        print("Execution de la séquence :", identifiant)
        if sequence:
            if priority:
                self.actions.inserer(sequence)
            else:
                for action in sequence:
                    print(action)
                    self.ajouter_action(action)
        else:
            print(f"⚠️ La séquence {identifiant} n'existe pas")

    # GESTION MENU

    def fermer_menu(self):
        """
        Ferme le menu actuel.
        """

        self.menu = None

    def ouvrir_menu(self, menu):
        """
        Ouvre un menu donné.
        :param menu: Le menu à ouvrir
        :return: None
        """

        self.menu = menu
        self.menu.ouvrir()

    # DEPLACEMENTS

    def simuler_segment(self, temps, region_dest, lieu_dest, simulation_temps, destination=False):
        """
        Simule un segment de déplacement en ajoutant des actions de temps et en exécutant des actions aléatoires.
        :param temps: Le temps total du segment
        :param region_dest: La région de destination
        :param lieu_dest: Le lieu de destination
        :param simulation_temps: Le temps de simulation actuel
        :param destination: Booléen, si c'est la destination finale
        :return: None
        """

        for _ in range(temps):

            chance = self.equipe.chance
            jour_sim, heure_sim = divmod(simulation_temps, 24)
            if heure_sim <= 5 or heure_sim >= 22:
                chance = chance * 0.75

            sequence = self.loader.tirer_action(chance)
            if sequence is not None:
                self.executer_sequence(sequence)

            simulation_temps += 1
            self.ajouter_action(AjoutTemps(self, {"type": "ajout-temps", "temps": 1}))

        self.ajouter_action(
            Deplacement(self, {
                "region": region_dest,
                "lieu": lieu_dest,
                "type": "deplacement",
                "destination": destination
            })
        )

    def deplacement(self, region, lieu):
        """
        Gère le déplacement du joueur vers une région et un lieu donnés en ajoutant les actions nécessaires à la file d'actions.
        :param region: La région de destination
        :param lieu: Le lieu de destination
        :return: None
        """

        self.action_actuelle.complete = True

        region_actuelle = self.get_region_actuelle()
        assert region_actuelle is not None

        print(f"deplacement vers {region}/{lieu}")
        print(f"depuis {region_actuelle.nom}/{self.lieu}")

        simulation_temps = self.temps

        if region != region_actuelle.nom:
            # vers entree
            if self.lieu != region_actuelle.entree:
                chemin, temps = region_actuelle.carte.paths(self.lieu, region_actuelle.entree)
                self.simuler_segment(
                    temps,
                    region_actuelle.nom,
                    region_actuelle.entree,
                    simulation_temps,
                    destination=False
                )

            # changement région
            chemin, temps = self.carte.paths(region_actuelle.nom, region)

            est_destination_finale = (lieu == self.regions[region].entree)
            self.simuler_segment(
                temps,
                region,
                self.regions[region].entree,
                simulation_temps,
                destination=est_destination_finale
            )

            # lieu final
            if not est_destination_finale:
                region_destination = self.regions[region]
                chemin, temps = region_destination.carte.paths(region_destination.entree, lieu)
                self.simuler_segment(
                    temps,
                    region,
                    lieu,
                    simulation_temps,
                    destination=True
                )
        else:
            # deplacement meme region
            chemin, temps = region_actuelle.carte.paths(self.lieu, lieu)
            self.simuler_segment(temps, region, lieu, simulation_temps, destination=True)