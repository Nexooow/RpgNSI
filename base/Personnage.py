import pygame
class Personnage:

    def __init__(self, equipe, parametres,x,y,image_sets, sprites,animation_steps,attacking_frames={},data=None):

        self.equipe = equipe
        self.nom = parametres["nom"]
        self.competences = parametres["competences"]

        self.attributs = {
            "vie_max": 100,
            "vie": 100,
            "force": 10,
            "vitesse": 10
        }
        self.arme = None
        self.size=image_sets[0]
        self.image_scale=image_sets[1]
        self.offset=image_sets[2]
        self.flip=False
        self.animation_list=self.load_frames(sprites[0],animation_steps)
        self.action=0
        self.frame_index=0
        self.image=self.animation_list[self.action][self.frame_index]
        self.update_time=pygame.time.get_ticks()
        self.rect=pygame.Rect((x,y,self.size/8*self.image_scale,180))
        self.bubble=pygame.image.load('blocking.png')
        self.x=x
        self.y=y
        self.running=False
        self.attacking=False
        self.alive=True
        self.attack_cooldown=0
        self.has_hit=False
        
        self.attack_frame=attacking_frames
        self.blocking=False
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
            attributs.update(self.arme["attributs"])
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
    def update_action(self,new_action):
        if new_action!=self.action:
            self.action=new_action
            self.frame_index=0
            self.update_time=pygame.time.get_ticks()
    def load_frames(self,sprite,animation_steps):
        animation_list=[]
        for y,anim in enumerate(sprite):
            temp_img_list=[]
            for i in range(animation_steps[y]):
                temp_img=sprite.subsurface(i*self.size,0,self.size,self.size)
                temp_img=pygame.transform.scale(temp_img,(self.size*self.image_scale,self.size*self.image_scale))
                temp_img_list.append(temp_img)
            animation_list.append(temp_img_list)
        return animation_list
    def draw(self,surface):
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
    def update(self,state,target=None):
        if self.attributs["vie"]<=0:
            self.alive=False
        self.update_action(state)
        animation_cooldown=50
        self.image=self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks()-self.update_time> animation_cooldown:
            self.frame_index+=1
            self.update_time=pygame.time.get_ticks()
        if self.frame_index>=len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index=len(self.animation_list[self.action])-1
            else:
                self.frame_index=0
                if self.action==3 or self.action==4:
                    self.attacking=False
                    self.attack_cooldown=20
                if self.action==5:
                    self.hit=False
                    self.attacking=False
                    self.attack_cooldown=20
        if self.attacking and not self.has_hit:
            if self.frame_index in self.attack_frame:
                self.apply_attack(target)
    def attack(self):
        self.attacking=True
        self.has_hit=False
    def apply_attack(self,target,a_distance=False):
        if target is None:
            return
        if not a_distance:
            offset_x=target.img_pos[0] - self.rect.left
            offset_y=target.img_pos[1] - self.rect.top
            overlap=self.mask.overlap(target.mask,(offset_x,offset_y))
            if overlap and not self.has_hit:
                target.health-=self.attributs["force"]
                self.has_hit=True
        else:
            target.health-=self.attributs["force"]
            self.has_hit=True
            


class Barman(Personnage):

    def __init__(self, equipe, x,y,data=None):
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
            [100,0.2,[0,0]] #Respectivement: la taille du perso, le scaling par rapport à l'image de base (500px de haut pour le barman), et l'offset à modifier si y a des petits problèmes au niveau de la diff d'affichage/hitbox
            ,[pygame.image.load("./assets/sprites/Barman_static.png"),pygame.image.load("./assets/sprites/Barman_throw_cocktail.png")],
            [1,3],
            {2},
            data
        )

    def utiliser_competence(self, combat, competence, cibles=None):
        match competence:
            case "flameche":
                self.update(0)
                self.draw(self.jeu.fond)
            case "tournee_generale":
                self.update(0)
                self.draw(self.jeu.fond)
            case "flambee":
                self.update(0)
                self.draw(self.jeu.fond)
            case "cocktail_molotov":
                self.update(1)
                self.draw(self.jeu.fond)
                
            case "double_shot":
                self.update(0)
                self.draw(self.jeu.fond)
            case "happy_hour":
                self.update(0)
                self.draw(self.jeu.fond)
            case "gueule_de_bois":
                self.update(0)
                self.draw(self.jeu.fond)
            case "dernier_verre":
                self.update(0)
                self.draw(self.jeu.fond)
            case "shot_enflamme":
                self.update(0)
                self.draw(self.jeu.fond)
            case "cuite_explosive":
                self.update(0)
                self.draw(self.jeu.fond)


class Vous(Personnage):

    def __init__(self, equipe, data=None):
        super().__init__(equipe, {
            "nom": "Vous",
            "competences": {
                "coup_de_poing": {
                    "nom": "Coup de Poing",
                    "description": "Frappe physique basique. Gagne 1 d'élan. Si la cible est Marquée, réapplique la marque.",
                    "cost": {
                        "pa": 2
                    },
                    "cible": "ennemi"
                },
                "marque": {
                    "nom": "Frappe marquante",
                    "description": "Applique une marque sur l'ennemi visé. Gagne 1 stack d'Élan.",
                    "cost": {
                        "pa": 2
                    },
                    "cible": "ennemi"
                },
                "charge_devastatrice": {
                    "nom": "Charge Dévastatrice",
                    "description": "Charge risquée vers un ennemi, infligeant des dégâts physiques importants. Passe la vie à 30%. Dégâts +15% par "
                                   "élan. Applique Étourdissement si +3 d'élan. Consomme tout l'élan.",
                    "cost": {
                        "pa": 3
                    },
                    "cible": "ennemi"
                },
                "broyeur": {
                    "nom": "Broyeur",
                    "description": "Frappe puissante qui applique vulnérabilité pour 2 tour. Si la cible "
                                   "est Marquée ou Étourdie, applique vulnérabilité 2. Gagne 2 stacks d'Élan.",
                    "cost": {
                        "pa": 4
                    },
                    "cible": "ennemi"
                },
                "riposte": {
                    "nom": "Riposte",
                    "description": "Posture défensive pour 2 tours. Contre-attaque automatiquement les ennemis qui vous "
                                   "frappent, infligeant 50% des dégâts reçu et appliquant Marqué I. Gagne 1 stack "
                                   "d'Élan par riposte.",
                    "cost": {
                        "pa": 3
                    },
                    "cible": None
                },
                "enchainement": {
                    "nom": "Enchaînement",
                    "description": "Série de 3 frappes rapides sur un ennemi. Chaque frappe inflige 20% de dégats en plus"
                                   "que la précédente. Si la cible est Marquée, la 3ème frappe applique "
                                   "Saignement II.",
                    "cost": {
                        "pa": 5
                    },
                    "cible": "ennemi"
                },
                "frappe_tactique": {
                    "nom": "Frappe tactique",
                    "description": "Attaque de précision qui inflige 50% de dégâts supplémentaires et ignore les boucliers. Si la cible est"
                                   "vulnérable, inflige 50% de dégats suplémentaires. Gagne 1 stack d'Élan.",
                    "cost": {
                        "pa": 4
                    },
                    "cible": "ennemi"
                },
                "furie_guerriere": {
                    "nom": "Furie Guerrière",
                    "description": "Augmente vos dégâts physiques de 30% et votre vitesse de 20% pour 3 tours."
                                   "Lors de l'activation, gagne immédiatement 2 stacks d'Élan.",
                    "cost": {
                        "pa": 5
                    },
                    "cible": "ennemi"
                },
                "execution": {
                    "nom": "Exécution",
                    "description": "Attaque dévastatrice qui inflige des dégâts massifs (+200% si la cible a moins de 30%"
                                   "PV). Coûte 5 d'élan.",
                    "cost": {
                        "pa": 8,
                        "elan": 5
                    },
                    "cible": "ennemi"
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
                    "cible": None
                },

            }
        }, data)

    def utiliser_competence(self, combat, competence, cibles=None):
        match competence:
            case "coup_de_poing":
                pass
            case "marque":
                pass
            case "charge_devastatrice":
                pass
            case "broyeur":
                pass
            case "riposte":
                pass
            case "enchainement":
                pass
            case "frappe_tactique":
                pass
            case "furie_guerriere":
                pass
            case "execution":
                pass
            case "onde_de_choc":
                pass


class Fachan(Personnage):

    def __init__(self, equipe, data=None):
        super().__init__(equipe, {
            "nom": "Fachan",
            "competences": {
                "regard_jugeur": {
                    "nom": "Regard jugeur",
                    "description": "Lance un regard jugeur aux ennemis, encaissant 90% des dégâts au prochain tour. Gagne un stack de mitigation.",
                    "cost": {"pa": 2},
                    "cible": None
                },
                "caisteal": {
                    "nom": "Caisteal",
                    "description": "Concentre toutes les attaques ennemies sur lui jusqu'à son prochain tour, gagne 30% de degats encaisses.",
                    "cost": {"pa": 4, "mitigation": 1},
                    "cible": None
                },
                "caber": {
                    "nom": "Caber",
                    "description": "lance sa massue sur un ennemi, 50% de chances de l'étourdir et 15% de chances que l'attaque se transmette à un autre ennemi",
                    "cost": {
                        "pa": 3
                    },
                    "cible": "ennemi"
                },
                "fureur_de_fachan": {
                    "nom": "Fureur de Fachan",
                    "description": "Diminue de 20% les dégâts pour chaque stack de mitigation possédé",
                    "cost": {
                        "pa": 0
                    },
                    "cible": None
                },
                "tignasse": {
                    "nom": "Tignasse",
                    "description": "Protège toute l'equipe avec sa chevelure. 15% de dommages en moins,",
                    "cost": {
                        "pa": 3},
                    "cible": None
                },
                "stalin": {
                    "nom": "Stalin",
                    "description": "Deviens l'Homme de Fer et encaisse tous les dégâts physiques pendant les trois prochains tours. Gagne un stack de mitigation",
                    "cost": {"pa": 4},
                    "cible": None
                },
                "ou_sont_mes_pieds": {
                    "nom": "Où sont mes pieds",
                    "description": "Cherche sa deuxième jambe, devient incapable d'attaquer mais récupère 50% de ses pv",
                    "cost": {"pa": 4},
                    "cible": None
                }
            }
        }, data)

    def utiliser_competence(self, combat, competence, cibles=None):
        match competence:
            case "regard_jugeur":
                pass
            case "caisteal":
                pass
            case "caber":
                pass
            case "fureur_de_fachan":
                pass
            case "tignasse":
                pass
            case "stalin":
                pass
            case "ou_sont_mes_pieds":
                pass
