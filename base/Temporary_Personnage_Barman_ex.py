import pygame

xp_par_niveaux = {}
for i in range(1, 101):
    xp_par_niveaux[i] = 100 * i


class Personnage:

    def __init__(self, equipe, parametres, x, y, image_sets, sprites, animation_steps, attacking_frames={}, data=None):

        self.equipe = equipe
        self.nom = parametres["nom"]
        self.competences = parametres["competences"]

        self.niveau = 1
        self.xp = 0

        self.attributs = {
            "vie_max": 100,
            "vie": 100,
            "force": 10,
            "vitesse": 10,
            "chance_critique": 10
        }

        self.arme = None
        self.size = image_sets[0]
        self.image_scale = image_sets[1]
        self.offset = image_sets[2]
        self.flip = False
        self.animation_list = self.load_frames(sprites, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, self.size / 8 * self.image_scale, 180))
        self.bubble = pygame.image.load('blocking.png')
        self.x = x
        self.y = y
        self.running = False
        self.attacking = False
        self.alive = True
        self.attack_cooldown = 0
        self.has_hit = False

        self.attack_frame = attacking_frames
        self.blocking = False
        self.current_competence=None
        self.target=None
        self.a_distance=False
        
        self.competences_equipes = []
        self.competences_debloques = []

        if data: self.restaurer(data)

    def restaurer(self, json):
        self.attributs = json["attributs"]
        self.arme = json["arme"]

        self.competences_equipes = json["competences_equipes"]
        self.competences_debloques = json["competences_debloques"]

    def sauvegarder(self):
        return {
            "nom": self.nom,
            "attributs": self.attributs,
            "arme": self.arme,
            "competences_equipes": self.competences_equipes,
            "competences_debloques": self.competences_debloques
        }

    def get_attributs(self):
        attributs = self.attributs.copy()
        if self.arme is not None:
            for nom_attribut, attribut in self.arme.attributs.items():
                attributs[nom_attribut] += attribut
        return attributs

    def equiper(self, item_id):
        arme = self.equipe.jeu.loader.items[item_id]
        if arme:
            self.arme = arme

    def utiliser(self, item):
        pass

    def infliger(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            # TODO: mort
            pass

    def soigner(self, points):
        self.vie = min(self.vie_max, self.vie + points)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def load_frames(self, sprite, animation_steps):
        animation_list = []
        for y, anim in enumerate(sprite):
            temp_img_list = []
            for i in range(animation_steps[y]):
                temp_img = anim.subsurface(i * self.size, 0, self.size, self.size)
                temp_img = pygame.transform.scale(temp_img,
                                                  (self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list

    def draw(self, surface):
        if self.blocking:
            self.bubble=pygame.transform.scale(self.bubble,(self.size*self.image_scale,self.size*self.image_scale))
            self.image=self.bubble
        img=pygame.transform.flip(self.image,self.flip,False)
        self.img_pos=(self.rect.x-(self.offset[0]*self.image_scale),self.rect.y-(self.offset[1]*self.image_scale))
        surface.blit(img,self.img_pos)
        self.mask=pygame.mask.from_surface(img)
    def move(self,x,y):
        self.rect.x=x
        self.rect.y=y 
    def update(self,state,a_distance=False,target=None):
        if self.attributs["vie"]<=0:
            self.alive=False
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
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20
        if self.attacking and not self.has_hit:
            if self.frame_index in self.attack_frame:
                self.apply_attack(target,a_distance)
    def attack(self):
        self.attacking=True
        self.has_hit=False
    def start_attack(self, action, a_distance=False, target=None):
        self.attacking = True
        self.has_hit = False
        self.a_distance = a_distance
        self.target = target
        self.update_action(action)
    def apply_attack(self,target,a_distance):
        if target is None:
            return
        if not a_distance:
            offset_x = target.img_pos[0] - self.rect.left
            offset_y = target.img_pos[1] - self.rect.top
            overlap = self.mask.overlap(target.mask, (offset_x, offset_y))
            if overlap and not self.has_hit:
                
                self.has_hit = True
                self.jeu.equipe.combat.on_hit(self,target)
        else:
            target.health -= self.attributs["force"]
            self.has_hit = True


class Barman(Personnage):

    def __init__(self, equipe, x, y, data=None):
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
                        "cible": "ennemi"
                    },
                    "tournee_generale": {
                        "nom": "Tournée Générale",
                        "description": "Applique Alcoolémie I à toutes les cibles (alliés et ennemis). Les alliés gagnent "
                                       "+10% de dégâts.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": None
                    },
                    "flambee": {
                        "nom": "Flambée",
                        "description": "Applique de légères brûlures à tous les ennemis. Les brûlures sont doublées"
                                       "par niveau d'alcoolémie de chaque cible. Consomme l'alcoolémie des ennemis.",
                        "cost": {
                            "pa": 6
                        },
                        "cible": None
                    },
                    "cocktail_molotov": {
                        "nom": "Cocktail Molotov",
                        "description": "Lance un cocktail enflammé sur un ennemi. Dégâts +15% par niveau d'alcoolémie "
                                       "du lanceur. Applique 3 brulures et 1 brulure sur chaque cible adjacente.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi"
                    },
                    "double_shot": {
                        "nom": "Double Shot",
                        "description": "Frappe un ennemi deux fois rapidement. Applique Alcoolémie I à la cible et augmente "
                                       "l'alcoolémie du lanceur de 1. Si la cible a déjà de l'alcoolémie, "
                                       "applique Étourdissement.",
                        "cost": {
                            "pa": 3
                        },
                        "cible": "ennemi"
                    },
                    "happy_hour": {
                        "nom": "Happy Hour",
                        "description": "Réduit le coût en PA de toutes les compétences alliées de 1 pour 3 tours. Applique "
                                       "Alcoolémie I à tous les alliés et augmente leurs dégâts élémentaires de 20%.",
                        "cost": {
                            "pa": 6
                        },
                        "cible": None
                    },
                    "gueule_de_bois": {
                        "nom": "Gueule de Bois",
                        "description": "Inflige des dégâts physiques massifs basés sur le niveau d'alcoolémie de la cible ("
                                       "x2.5 par niveau) et la rend vulnérable (-20% résistances) pour 2 tours. Réinitialise "
                                       "son alcoolémie à 0.",
                        "cost": {
                            "pa": 5
                        },
                        "cible": "ennemi"
                    },
                    "dernier_verre": {
                        "nom": "Le Dernier Verre",
                        "description": "Attaque dévastatrice. Dégâts basés sur l'alcoolémie consommée. Applique 3 brulures à "
                                       "toutes les cibles.",
                        "cost": {
                            "pa": 8,
                            "alcoolemie": 3
                        },
                        "cible": "ennemi"
                    },
                    "shot_enflamme": {
                        "nom": "Shot Enflammé",
                        "description": "Enflamme un ennemi et lui applique Alcoolémie II. Si la cible a "
                                       "déjà de l'alcoolémie, applique 5 brulures.",
                        "cost": {
                            "pa": 4
                        },
                        "cible": "ennemi"
                    },
                    "cuite_explosive": {
                        "nom": "Cuite Explosive",
                        "description": "Convertit chaque niveau d'alcoolémie du lanceur en dégâts de zone explosifs "
                                       "sur tous les ennemis. Applique 10 brulures par niveau d'alcoolémie "
                                       "consommé. Réinitialise l'alcoolémie.",
                        "cost": {
                            "pa": 7
                        },
                    }
                }
            },
            x,
            y,
            [100, 0.2, [0, 0]]
            # Respectivement: la taille du perso, le scaling par rapport à l'image de base (500px de haut pour le barman), et l'offset à modifier si y a des petits problèmes au niveau de la diff d'affichage/hitbox
            , [pygame.image.load("./assets/sprites/Barman_static.png"),
               pygame.image.load("./assets/sprites/Barman_throw_cocktail.png")],
            [1, 3],
            {2},
            data
        )
    
            
        
        
    def play_competence(self,competence_id, target=None):
        match competence_id:
            case "flameche":
                pass
            case "tournee_generale":
                pass
            case "flambee":
                pass
            case "cocktail_molotov":
                self.start_attack(action=1,a_distance=True,target=target)

            case "double_shot":
                pass
            case "happy_hour":
                pass
            case "gueule_de_bois":
                pass
            case "dernier_verre":
                pass
            case "shot_enflamme":
                pass
            case "cuite_explosive":
                pass
