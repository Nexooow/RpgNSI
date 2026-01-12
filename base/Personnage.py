import pygame
import random
from lib.combat import add_effets, calcul_degats

XP_PAR_NIVEAUX = {i: 100 * i for i in range(1, 101)}


class Personnage:
    """
    Classe de base pour tous les personnages du jeu.
    """

    def __init__(self, equipe, parametres, x, y, image_sets, sprites, animation_steps, attacking_frames=None,
                 data=None):
        """
        Initialise un personnage avec ses paramètres de base.
        """
        # Attributs principaux
        self.equipe = equipe
        self.nom = parametres["nom"]
        self.competences = parametres["competences"]
        self.niveau = 1
        self.xp = 0
        self.points_competences = 1
        self.points_attributs = 0

        # Attributs liés aux statistiques
        self.attributs = {
            "vie_max": 100,
            "vie": 100,
            "force": 10,
            "vitesse": 10,
            "chance_critique": 10
        }
        self.arme = None

        # Gestion des animations
        self.size = image_sets[0]
        self.image_scale = image_sets[1]
        self.offset = image_sets[2]
        self.flip = False
        self.animation_list = self.load_frames(sprites, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.bubble = pygame.image.load('./assets/sprites/blocking.png')

        # Position et état
        self.x = x
        self.y = y
        self.running = False
        self.attacking = False
        self.alive = True
        self.attack_cooldown = 0
        self.has_hit = False
        self.attack_frame = attacking_frames
        self.blocking = False
        self.current_competence = None
        self.target = None
        self.a_distance = False

        # Compétences
        self.competences_equipes = []
        self.competences_debloques = []

        if data:
            self.restaurer(data)

    def restaurer(self, json):
        """Restaure les données d'un personnage à partir d'un JSON."""
        self.attributs = json["attributs"]
        self.arme = json["arme"]
        self.competences_equipes = json["competences_equipes"]
        self.competences_debloques = json["competences_debloques"]

    def sauvegarder(self):
        """Sauvegarde les données du personnage dans un dictionnaire."""
        return {
            "nom": self.nom,
            "attributs": self.attributs,
            "arme": self.arme,
            "competences_equipes": self.competences_equipes,
            "competences_debloques": self.competences_debloques
        }

    def ajouter_xp(self, xp):
        """Ajoute de l'expérience au personnage et gère les niveaux."""
        self.xp += xp
        if self.xp > XP_PAR_NIVEAUX[self.niveau + 1]:
            self.xp -= XP_PAR_NIVEAUX[self.niveau + 1]
            self.niveau += 1
            self.points_attributs += 3
            self.points_competences += 1

    def get_attributs(self):
        """Retourne les attributs du personnage, en tenant compte de l'arme équipée."""
        attributs = self.attributs.copy()
        if self.arme is not None:
            for nom_attribut, attribut in self.arme.attributs.items():
                attributs[nom_attribut] += attribut
        return attributs

    def equiper(self, item_id):
        """Équipe une arme à partir de son ID."""
        arme = self.equipe.jeu.loader.items[item_id]
        if arme:
            self.arme = arme

    def infliger(self, degats):
        """Inflige des dégâts au personnage."""
        self.attributs["vie"] -= degats
        if self.attributs["vie"] <= 0:
            self.alive = False

    def soigner(self, points):
        """Soigne le personnage."""
        self.attributs["vie"] = min(self.attributs["vie_max"], self.attributs["vie"] + points)

    def update_action(self, new_action):
        """Met à jour l'action actuelle du personnage."""
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def load_frames(self, sprite, animation_steps):
        """Charge les frames d'animation pour le personnage."""
        animation_list = []
        for y, anim in enumerate(sprite):
            width, height = anim.get_size()
            frame_width = width // animation_steps[y]
            frame_height = height
            temp_img_list = []
            for i in range(animation_steps[y]):
                temp_img = anim.subsurface(
                    i * frame_width,
                    0,
                    frame_width,
                    frame_height
                )
                temp_img = pygame.transform.scale(
                    temp_img,
                    (
                        int(frame_width * self.image_scale),
                        int(frame_height * self.image_scale)
                    )
                )
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list

    def draw(self):
        """Dessine le personnage à l'écran."""
        if self.blocking:
            self.bubble = pygame.transform.scale(
                self.bubble,
                (self.size * self.image_scale, self.size * self.image_scale)
            )
            self.image = self.bubble
        img = pygame.transform.flip(self.image, self.flip, False)
        self.img_pos = (
            self.rect.x - (self.offset[0] * self.image_scale),
            self.rect.y - (self.offset[1] * self.image_scale)
        )
        self.equipe.jeu.ui_surface.blit(img, self.img_pos)
        self.mask = pygame.mask.from_surface(img)

    def move(self, x, y):
        """Déplace le personnage."""
        self.rect.x = x
        self.rect.y = y

    def update(self, state):
        """Met à jour l'état du personnage."""
        if self.attributs["vie"] <= 0:
            self.alive = False
        self.update_action(state)
        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                self.update_action(0)
        if self.attacking and not self.has_hit:
            if self.frame_index in self.attack_frame[self.action]:
                self.apply_attack()

    def attack(self):
        """Déclenche une attaque."""
        self.attacking = True
        self.has_hit = False

    def start_attack(self, action, a_distance=False, target=None):
        """Initialise une attaque."""
        self.attacking = True
        self.has_hit = False
        self.a_distance = a_distance
        self.target = target
        self.update_action(action)

    def apply_attack(self):
        """Applique les effets d'une attaque."""
        self.has_hit = True


class Vous(Personnage):
    """
    Classe représentant le joueur principal.
    """

    def __init__(self, equipe, data=None):
        super().__init__(
            equipe,
            {
                "nom": "Vous",
                "competences": {
                    "coup_de_poing": {
                        "nom": "Coup de Poing",
                        "description": "Frappe physique basique. Gagne 1 d'élan. Si la cible est Marquée, réapplique la marque.",
                        "cost": {
                            "pa": 2
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "marque": {
                        "nom": "Frappe marquante",
                        "description": "Applique une marque sur l'ennemi visé. Gagne 1 stack d'Élan.",
                        "cost": {
                            "pa": 2
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "charge_devastatrice": {
                        "nom": "Charge Dévastatrice",
                        "description": "Charge risquée vers un ennemi, infligeant des dégâts physiques importants. Passe la vie à 30%. Dégâts +15% par "
                                       "élan. Applique Étourdissement si +3 d'élan. Consomme tout l'élan.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "broyeur": {
                        "nom": "Broyeur",
                        "description": "Frappe puissante qui applique vulnérabilité pour 2 tour. Si la cible "
                                       "est Marquée ou Étourdie, applique vulnérabilité 2. Gagne 2 stacks d'Élan.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "riposte": {
                        "nom": "Riposte",
                        "description": "Posture défensive pour 2 tours. Contre-attaque automatiquement les ennemis qui vous "
                                       "frappent, infligeant 50% des dégâts reçu et appliquant Marqué I. Gagne 1 stack "
                                       "d'Élan par riposte.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": None,
                        "points": 1
                    },
                    "enchainement": {
                        "nom": "Enchaînement",
                        "description": "Série de 3 frappes rapides sur un ennemi. Chaque frappe inflige 20% de dégats en plus"
                                       "que la précédente. Si la cible est Marquée, la 3ème frappe applique "
                                       "Saignement II.",
                        "cost": {
                            "pa": 5
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "frappe_tactique": {
                        "nom": "Frappe tactique",
                        "description": "Attaque de précision qui inflige 50% de dégâts supplémentaires et ignore les boucliers. Si la cible est"
                                       "vulnérable, inflige 50% de dégats suplémentaires. Gagne 1 stack d'Élan.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "furie_guerriere": {
                        "nom": "Furie Guerrière",
                        "description": "Augmente vos dégâts physiques de 30% et votre vitesse de 20% pour 3 tours."
                                       "Lors de l'activation, gagne immédiatement 2 stacks d'Élan.",
                        "cost": {
                            "pa": 5
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "execution": {
                        "nom": "Exécution",
                        "description": "Attaque dévastatrice qui inflige des dégâts massifs (+200% si la cible a moins de 30%"
                                       "PV). Coûte 5 d'élan.",
                        "cost": {
                            "pa": 8,
                            "elan": 5
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "onde_de_choc": {
                        "nom": "Onde de Choc",
                        "description": "Frappe le sol, créant une onde qui inflige des dégâts physiques à tous les "
                                       "ennemis. Dégâts +10% par stack d'Élan possédé. Applique Marqué I à toutes les "
                                       "cibles touchées. Consomme tous les stacks d'Élan (minimum 2 requis).",
                        "cost": {
                            "pa": 6,
                            "elan": 2
                        },
                        "cible": None,
                        "points": 1
                    },

                }
            },
            50,
            50,
            [100, 0.6, [0, 0]],
            [
                pygame.image.load("./assets/sprites/Idle.png"),
                pygame.image.load("./assets/sprites/Run.png"),
                pygame.image.load("./assets/sprites/Jump.png"),
                pygame.image.load("./assets/sprites/Attack1.png"),
                pygame.image.load("./assets/sprites/Attack3.png"),
                pygame.image.load("./assets/sprites/blocking.png"),
                pygame.image.load("./assets/sprites/Death.png")
            ],
            [10, 8, 1, 7, 8, 1, 7],
            {0: [0], 3: [4], 4: [4], 5: [0]},
            # 0:idle, 1:running, 2:jumping, 3:slash from downwards, 4:slash from upwards, 5:getting hit,6:dying
            data
        )
        self.competences_debloques = ["marque", "coup_de_poing"]
        self.competences_equipes = ["marque", "coup_de_poing"]

    def utiliser_competence(self, competence, attaquant, target=None):
        """Utilise une compétence du joueur."""
        if competence == "coup_de_poing":
            self.start_attack(action=3, a_distance=False, target=target)
            degats = calcul_degats(attaquant, target)
            target["vie"] -= degats
            add_effets(attaquant, {"elan": [1, -1]})
            if "marque" in target.get("effets", {}):
                add_effets(target, {"marque": [1, 3]})
        elif competence == "marque":
            self.start_attack(action=3, a_distance=False, target=target)
            add_effets(attaquant, {"elan": [1, 2]})
            add_effets(target, {"marque": [1, 3]})
        elif competence == "charge_devastatrice":
            self.start_attack(action=4, a_distance=False, target=target)
            self.attributs["vie"] = max(int(self.attributs["vie_max"] * 0.3), 1)
            degats = calcul_degats(attaquant, target) * (1 + 0.15 * attaquant["effets"].get("elan", [0])[0])
            target["vie"] -= degats
            if self.attributs.get("elan", 0) >= 3:
                add_effets(target, {"etourdissement": [1, 1]})
            self.attributs["elan"] = 0
        elif competence == "broyeur":
            self.start_attack(action=3, a_distance=False, target=target)
            add_effets(target, {"vulnerabilite": [1, 2]})
            if "marque" in target.get("effets", {}) or "etourdissement" in target.get("effets", {}):
                add_effets(target, {"vulnerabilite": [2, 2]})
            add_effets({
                attaquant,
                {
                    "elan": [2, -1]
                }
            })
        elif competence == "riposte":
            self.start_attack(action=5, a_distance=False, target=target)
            add_effets(attaquant, {"riposte": [1, 2]})
        elif competence == "enchainement":
            self.start_attack(action=3, a_distance=False, target=target)
            degats = calcul_degats(attaquant, target)
            for i in range(3):
                target["vie"] -= degats * (1 + 0.2 * i)
            if "marque" in target.get("effets", {}):
                add_effets(target, {"saignement": [2, 3]})
        elif competence == "frappe_tactique":
            self.start_attack(action=3, a_distance=False, target=target)
            degats = calcul_degats(attaquant, target) * 1.5
            if "vulnerabilite" in target.get("effets", {}):
                degats *= 1.5
            target["vie"] -= degats
            add_effets({
                attaquant,
                {
                    "elan": [1, -1]
                }
            })
        elif competence == "furie_guerriere":
            self.start_attack(action=1, a_distance=False, target=target)
            add_effets(self, {"bonus_degats": [0.3, 3], "bonus_vitesse": [0.2, 3]})
            add_effets({
                attaquant,
                {
                    "elan": [2, -1]
                }
            })
        elif competence == "execution":
            self.start_attack(action=4, a_distance=False, target=target)
            if self.attributs.get("elan", 0) >= 5:
                degats = calcul_degats(self, target) * (3 if target["vie"] < target["vie_max"] * 0.3 else 1)
                target["vie"] -= degats
                attaquant["effets"]["elan"][0] -= 5
        elif competence == "onde_de_choc":
            self.start_attack(action=4, a_distance=False, target=target)
            if self.attributs.get("elan", 0) >= 2:
                for ennemi in target[1]:
                    degats = calcul_degats(self, ennemi) * (1 + 0.1 * self.attributs["elan"])
                    ennemi["vie"] -= degats
                    add_effets(ennemi, {"marque": [1, 3]})
                self.attributs["elan"] = 0


class Barman(Personnage):
    """
    Classe représentant le personnage Barman, avec des compétences spécifiques.
    """

    def __init__(self, equipe, data=None):
        super().__init__(
            equipe,
            {
                "nom": "Barman",
                "competences": {
                    "flameche": {
                        "nom": "Flameche",
                        "description": "Lance une petite flamme sur un ennemi, infligeant des dégâts de feu légers. "
                                       "Inflige une brulure par niveau d'alcoolémie.",
                        "cost": {
                            "pa": 2
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "tournee_generale": {
                        "nom": "Tournée Générale",
                        "description": "Applique Alcoolémie I à toutes les cibles (alliés et ennemis). Les alliés gagnent "
                                       "+10% de dégâts.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": None,
                        "points": 1
                    },
                    "flambee": {
                        "nom": "Flambée",
                        "description": "Applique de légères brûlures à tous les ennemis. Les brûlures sont doublées"
                                       "par niveau d'alcoolémie de chaque cible. Consomme l'alcoolémie des ennemis.",
                        "cost": {
                            "pa": 6
                        },
                        "cible": None,
                        "points": 1
                    },
                    "cocktail_molotov": {
                        "nom": "Cocktail Molotov",
                        "description": "Lance un cocktail enflammé sur un ennemi. Dégâts +15% par niveau d'alcoolémie "
                                       "du lanceur. Applique 3 brulures.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "double_shot": {
                        "nom": "Double Shot",
                        "description": "Frappe un ennemi deux fois rapidement. Applique Alcoolémie I à la cible et augmente "
                                       "l'alcoolémie du lanceur de 1. Si la cible a déjà de l'alcoolémie, "
                                       "applique Étourdissement.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "happy_hour": {
                        "nom": "Happy Hour",
                        "description": "Réduit le coût en PA de toutes les compétences alliées de 1 pour 3 tours. Applique "
                                       "Alcoolémie I à tous les alliés.",
                        "cost": {
                            "pa": 6
                        },
                        "cible": None,
                        "points": 1
                    },
                    "gueule_de_bois": {
                        "nom": "Gueule de Bois",
                        "description": "Inflige des dégâts physiques massifs basés sur le niveau d'alcoolémie de la cible ("
                                       "x2.5 par niveau). Réinitialise son alcoolémie à 0. Met la santé du lanceur à 1.",
                        "cost": {
                            "pa": 8
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "shot_enflamme": {
                        "nom": "Shot Enflammé",
                        "description": "Enflamme un ennemi et lui applique Alcoolémie II. Si la cible a "
                                       "déjà de l'alcoolémie, applique 5 brulures.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "cuite_explosive": {
                        "nom": "Cuite Explosive",
                        "description": "Convertit chaque niveau d'alcoolémie du lanceur en dégâts de zone explosifs "
                                       "sur tous les ennemis. Applique 5 brulures par niveau d'alcoolémie "
                                       "consommé. Réinitialise l'alcoolémie.",
                        "cost": {
                            "pa": 8
                        },
                        "points": 1
                    }
                }
            },
            50,
            200,
            [100, 0.2, [0, 0]],
            # Respectivement : la taille du perso, le scaling par rapport à l'image de base (500px de haut pour le barman), et l'offset à modifier si y a des petits problèmes au niveau de la diff d'affichage/hitbox
            [
                pygame.image.load("./assets/sprites/Barman_static.png"),
                pygame.image.load("./assets/sprites/Barman_throw_cocktail.png")
            ],
            [1, 3],
            {0: [0], 1: [2]},
            data
        )
        self.competences_debloques = ["double_shot", "cocktail_molotov"]
        self.competences_equipes = ["double_shot", "cocktail_molotov"]

    def utiliser_competence(self, competence_id, attaquant, target=None):
        """Utilise une compétence du Barman."""
        if competence_id == "flameche":
            self.start_attack(action=1, a_distance=True, target=target)
            add_effets(
                target,
                {
                    "brulure": [1 + target["effets"].get("alcoolemie", [0])[0], 3]
                }
            )
        elif competence_id == "tournee_generale":
            self.start_attack(action=0, a_distance=True, target=target)
            assert isinstance(target, list)
            for cible in target[0] + target[1]:
                add_effets(
                    cible,
                    {
                        "alcoolemie": [1, 3]
                    }
                )
        elif competence_id == "flambee":
            self.start_attack(action=0, a_distance=True, target=target)
            assert isinstance(target, list)
            for cible in target[1]:
                add_effets(
                    cible,
                    {
                        "brulure": [1 * (2 * cible["effets"].get("alcoolemie", [0])), 3]
                    }
                )
                if "alcoolemie" in cible["effets"]:
                    del cible["effets"]["alcoolemie"]
        elif competence_id == "cocktail_molotov":
            print("Utilisation de Cocktail Molotov")
            self.start_attack(action=1, a_distance=True, target=target)
            degats = calcul_degats(attaquant, target)
            target["vie"] -= degats * (1 + 0.15 * attaquant["effets"].get("alcoolemie", [0])[0])
            add_effets(
                target,
                {
                    "brulure": [3, 3]
                }
            )
        elif competence_id == "double_shot":
            self.start_attack(action=1, a_distance=True, target=target)
            if "alcoolemie" in target["effets"]:
                add_effets(
                    target,
                    {
                        "etourdissement": [1, 1]
                    }
                )
            add_effets(
                target,
                {
                    "alcoolemie": [1, 3]
                }
            )
            add_effets(attaquant, {"alcoolemie": [1, 3]})
            degats = calcul_degats(attaquant, target)
            target["vie"] -= degats
        elif competence_id == "happy_hour":
            self.start_attack(action=0, a_distance=True, target=target)
            assert isinstance(target, list)
            for cible in target[0]:
                add_effets(
                    cible,
                    {
                        "reduction_pa": [1, 3],
                        "alcoolemie": [1, 3]
                    }
                )
        elif competence_id == "gueule_de_bois":
            self.start_attack(action=1, a_distance=True, target=target)
            degats = calcul_degats(attaquant, target) * 3
            target["vie"] -= degats * (2.5 * target["effets"].get("alcoolemie", [0])[0])
            attaquant["attributs"]["vie"] = 1
        elif competence_id == "shot_enflamme":
            self.start_attack(action=1, a_distance=True, target=target)
            add_effets(
                target,
                {
                    "alcoolemie": [2, 3],
                    "brulure": [5 if "alcoolemie" in target["effets"] else 1, 3]
                }
            )
        elif competence_id == "cuite_explosive":
            assert isinstance(target, list)
            niveau_alcoolemie = attaquant["effets"].get("alcoolemie", [0])[0]
            for cible in target[1]:
                add_effets(
                    cible,
                    {
                        "brulure": [5 * niveau_alcoolemie, 3]
                    }
                )
            if "alcoolemie" in attaquant["effets"]:
                del attaquant["effets"]["alcoolemie"]


class Fachan(Personnage):
    """
    Classe représentant le personnage Fachan, avec des compétences spécifiques.
    """

    def __init__(self, equipe, data=None):
        super().__init__(
            equipe,
            {
                "nom": "Fachan",
                "competences": {
                    "regard_jugeur": {
                        "nom": "Regard jugeur",
                        "description": "Lance un regard jugeur aux ennemis, encaissant 90% des dégâts au prochain "
                                       "tour. Gagne un stack de mitigation.",
                        "cost": {
                            "pa": 2
                        },
                        "cible": None,
                        "points": 1
                    },
                    "caisteal": {
                        "nom": "Caisteal",
                        "description": "Concentre toutes les attaques ennemies sur lui jusqu'à son prochain tour, "
                                       "gagne 30% de degats encaisses.",
                        "cost": {
                            "pa": 4, "mitigation": 1
                        },
                        "cible": None,
                        "points": 1
                    },
                    "caber": {
                        "nom": "Caber",
                        "description": "lance sa massue sur un ennemi, 50% de chances de l'étourdir et 15% de chances "
                                       "que l'attaque se transmette à un autre ennemi",
                        "cost": {
                            "pa": 3
                        },
                        "cible": "ennemi",
                        "points": 1
                    },
                    "fureur_de_fachan": {
                        "nom": "Fureur de Fachan",
                        "description": "Diminue de 20% les dégâts pour chaque stack de mitigation possédé",
                        "cost": {
                            "pa": 0
                        },
                        "cible": None,
                        "points": 1
                    },
                    "tignasse": {
                        "nom": "Tignasse",
                        "description": "Protège toute l'equipe avec sa chevelure. 15% de dommages en moins,",
                        "cost": {
                            "pa": 3
                        },
                        "cible": None,
                        "points": 1
                    },
                    "stalin": {
                        "nom": "Stalin",
                        "description": "Deviens l'Homme de Fer et encaisse tous les dégâts physiques pendant les "
                                       "trois prochains tours. Gagne un stack de mitigation",
                        "cost": {
                            "pa": 4
                        },
                        "cible": None,
                        "points": 1
                    },
                    "ou_sont_mes_pieds": {
                        "nom": "Où sont mes pieds",
                        "description": "Cherche sa deuxième jambe, devient incapable d'attaquer mais récupère 50% de "
                                       "ses pv",
                        "cost": {
                            "pa": 4
                        },
                        "cible": None,
                        "points": 1
                    }
                }
            },
            50,
            350,
            [100, 0.25, [0, 0]],
            [
                pygame.transform.flip(
                    pygame.transform.scale(
                        pygame.image.load('./assets/sprites/fachan_static_steel-removebg-preview.png'),
                        (int((408 / 1024) * 1536), 408)
                    ),
                    True,
                    False
                ),
                pygame.transform.flip(
                    pygame.transform.scale(
                        pygame.image.load("./assets/sprites/fachan_static-removebg-preview.png"),
                        (int((408 / 1024) * 1536), 408)
                    ),
                    True,
                    False
                ),
                pygame.transform.flip(
                    pygame.image.load("./assets/sprites/fachan-removebg-preview (2).png"),
                    True,
                    False
                ),
                pygame.transform.flip(
                    pygame.image.load("./assets/sprites/fachan_steelform_attacking.png"),
                    True,
                    False
                ),
                pygame.transform.flip(
                    pygame.image.load("./assets/sprites/look_for_feet.png"),
                    True,
                    False
                ),
                pygame.transform.flip(
                    pygame.transform.scale(
                        pygame.image.load("./assets/sprites/look_for_feet_steel.png"),
                        (int((408 / 100) * 97), 100)
                    ),
                    True,
                    False
                ),
            ],
            [1, 1, 3, 3, 1, 1],
            {0: [0], 1: [0], 2: [2], 3: [2], 4: [0], 5: [0]},
            data)
        self.steel_form = False
        self.competences_debloques = ["regard_jugeur", "caber"]
        self.competences_equipes = ["regard_jugeur", "caber"]

    def utiliser_competence(self, competence, attaquant, cibles=None):
        """Utilise une compétence de Fachan."""
        if competence == "regard_jugeur":
            self.start_attack(1, a_distance=True, target=cibles) if self.steel_form else self.start_attack(0,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            add_effets(self, {"mitigation": [1, 1]})
        elif competence == "caisteal":
            self.start_attack(1, a_distance=True, target=cibles) if self.steel_form else self.start_attack(0,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            add_effets(self, {"provocation": [1, 1], "reduction_degats": [0.3, 1]})
        elif competence == "caber":
            self.start_attack(3, a_distance=True, target=cibles) if self.steel_form else self.start_attack(2,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            degats = calcul_degats(self, cibles)
            cibles["vie"] -= degats
            if random.random() < 0.5:
                add_effets(cibles, {"etourdissement": [1, 1]})
        elif competence == "fureur_de_fachan":
            self.start_attack(1, a_distance=True, target=cibles) if self.steel_form else self.start_attack(0,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            mitigation = self.attributs.get("mitigation", 0)
            add_effets(attaquant, {"reduction_degats": [0.2 * mitigation, 1]})
        elif competence == "tignasse":
            self.start_attack(1, a_distance=True, target=cibles) if self.steel_form else self.start_attack(0,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            for cible in cibles:
                add_effets(cible, {"reduction_degats": [0.15, 1]})
        elif competence == "stalin":
            self.steel_form = True
            add_effets(attaquant, {"invulnerabilite_physique": [1, 3], "mitigation": [1, 3]})
        elif competence == "ou_sont_mes_pieds":
            self.start_attack(5, a_distance=True, target=cibles) if self.steel_form else self.start_attack(4,
                                                                                                           a_distance=True,
                                                                                                           target=cibles)
            attaquant["attributs"]["vie"] = min(
                attaquant["attributs"]["vie_max"],
                attaquant["attributs"]["vie"] + int(attaquant["attributs"]["vie_max"] * 0.5)
            )
            self.blocking = True