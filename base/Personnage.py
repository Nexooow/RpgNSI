class Personnage:

    def __init__(self, equipe, parametres, data=None):
        self.equipe = equipe
        self.nom = parametres["nom"]

        self.vie_max = 100
        self.vie = 100
        self.force = 10
        self.vitesse = 10

        self.arme = None

        self.competences_equipes = []
        self.competences_debloques = []
        self.competences = parametres["competences"]

    def est_mort(self):
        return self.vie <= 0

    def restaurer(self, json):
        self.vie_max = json["vie_max"]
        self.vie = json["vie"]
        self.force = json["force"]
        self.vitesse = json["vitesse"]

        self.arme = json["arme"]

        self.competences_equipes = json["competences_equipes"]
        self.competences_debloques = json["competences_debloques"]

    # TODO: système de compétences (avec arbre)
    # TODO: attributs du personnage (force, vitesse, chance, resistance ...)

    def equiper(self, item_id):
        if self.arme:
            self.desequiper()
        # TODO: équiper l'arme et ajouter les bonus

    def desequiper(self):
        if self.arme is not None:
            # TODO: retirer les bonus de l'arme
            self.arme = None

    def utiliser(self, item):
        pass

    def infliger(self, degats):
        self.vie -= degats
        if self.vie <= 0:
            # TODO: mort
            pass

    def soigner(self, points):
        self.vie = min(self.vie_max, self.vie + points)


class Barman(Personnage):

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
                        "points": 0
                    },
                    "tournee_generale": {
                        "nom": "Tournée Générale",
                        "description": "Applique Alcoolémie I à toutes les cibles (alliés et ennemis). Les alliés gagnent "
                                       "+10% de dégâts.",
                        "cost": {
                            "pa": 3
                        },
                    },
                    "flambee": {
                        "nom": "Flambée",
                        "description": "Applique de légères brûlures à tous les ennemis. Les brûlures sont doublées"
                                       "par niveau d'alcoolémie de chaque cible. Consomme l'alcoolémie des ennemis.",
                        "cost": {
                            "pa": 6
                        },
                    },
                    "cocktail_molotov": {
                        "nom": "Cocktail Molotov",
                        "description": "Lance un cocktail enflammé sur un ennemi. Dégâts +15% par niveau d'alcoolémie "
                                       "du lanceur. Applique 3 brulures et 1 brulure sur chaque cible adjacente.",
                        "cost": {
                            "pa": 4
                        },
                    },
                    "double_shot": {
                        "nom": "Double Shot",
                        "description": "Frappe un ennemi deux fois rapidement. Applique Alcoolémie I à la cible et augmente "
                                       "l'alcoolémie du lanceur de 1. Si la cible a déjà de l'alcoolémie, "
                                       "applique Étourdissement.",
                        "cost": {
                            "pa": 3
                        },
                    },
                    "happy_hour": {
                        "nom": "Happy Hour",
                        "description": "Réduit le coût en PA de toutes les compétences alliées de 1 pour 3 tours. Applique "
                                       "Alcoolémie I à tous les alliés et augmente leurs dégâts élémentaires de 20%.",
                        "cost": {
                            "pa": 6
                        },
                    },
                    "gueule_de_bois": {
                        "nom": "Gueule de Bois",
                        "description": "Inflige des dégâts physiques massifs basés sur le niveau d'alcoolémie de la cible ("
                                       "x2.5 par niveau) et la rend vulnérable (-20% résistances) pour 2 tours. Réinitialise "
                                       "son alcoolémie à 0.",
                        "cost": {
                            "pa": 5
                        },
                    },
                    "dernier_verre": {
                        "nom": "Le Dernier Verre",
                        "description": "Attaque dévastatrice. Dégâts basés sur l'alcoolémie consommée. Applique 3 brulures à "
                                       "toutes les cibles.",
                        "cost": {
                            "pa": 8,
                            "alcoolemie": 3
                        },
                    },
                    "shot_enflamme": {
                        "nom": "Shot Enflammé",
                        "description": "Enflamme un ennemi et lui applique Alcoolémie II. Si la cible a "
                                       "déjà de l'alcoolémie, applique 5 brulures.",
                        "cost": {
                            "pa": 4
                        },
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
            data
        )


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
                },
                "marque": {
                    "nom": "Frappe marquante",
                    "description": "Applique une marque sur l'ennemi visé. Gagne 1 stack d'Élan.",
                    "cost": {
                        "pa": 2
                    },
                },
                "charge_devastatrice": {
                    "nom": "Charge Dévastatrice",
                    "description": "Charge risquée vers un ennemi, infligeant des dégâts physiques importants. Passe la vie à 30%. Dégâts +15% par "
                                   "élan. Applique Étourdissement si +3 d'élan. Consomme tout l'élan.",
                    "cost": {
                        "pa": 3
                    },
                },
                "broyeur": {
                    "nom": "Broyeur",
                    "description": "Frappe puissante qui applique vulnérabilité pour 2 tour. Si la cible "
                                   "est Marquée ou Étourdie, applique vulnérabilité 2. Gagne 2 stacks d'Élan.",
                    "cost": {
                        "pa": 4
                    },
                },
                "riposte": {
                    "nom": "Riposte",
                    "description": "Posture défensive pour 2 tours. Contre-attaque automatiquement les ennemis qui vous "
                                   "frappent, infligeant 50% des dégâts reçu et appliquant Marqué I. Gagne 1 stack "
                                   "d'Élan par riposte.",
                    "cost": {
                        "pa": 3
                    },
                },
                "enchaînement": {
                    "nom": "Enchaînement",
                    "description": "Série de 3 frappes rapides sur un ennemi. Chaque frappe inflige 20% de dégats en plus"
                                   "que la précédente. Si la cible est Marquée, la 3ème frappe applique "
                                   "Saignement II.",
                    "cost": {
                        "pa": 5
                    },
                },
                "frappe_tactique": {
                    "nom": "Frappe tactique",
                    "description": "Attaque de précision qui inflige 50% de dégâts supplémentaires et ignore les boucliers. Si la cible est"
                                   "vulnérable, inflige 50% de dégats suplémentaires. Gagne 1 stack d'Élan.",
                    "cost": {
                        "pa": 4
                    },
                },
                "furie_guerriere": {
                    "nom": "Furie Guerrière",
                    "description": "Augmente vos dégâts physiques de 30% et votre vitesse de 20% pour 3 tours."
                                   "Lors de l'activation, gagne immédiatement 2 stacks d'Élan.",
                    "cost": {
                        "pa": 5
                    },
                },
                "execution": {
                    "nom": "Exécution",
                    "description": "Attaque dévastatrice qui inflige des dégâts massifs (+200% si la cible a moins de 30%"
                                   "PV). Coûte 5 d'élan.",
                    "cost": {
                        "pa": 8,
                        "elan": 5
                    },
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
                },

            }
        })
class Fachan(Personnage):
    def __init__(self,equipe,data=None):
        super().__init__(equipe,{
            "nom":"Fachan",
            "competences":{
                "Regard jugeur":{
                    "nom":"Regard jugeur",
                    "description":"Lance un regard jugeur aux ennemis, encaissant 90% des dégâts au prochain tour. Gagne un stack de mitigation.",
                    "cost":{"pa":2}                },
                
                    "Caisteal":{
                        "nom":"Caisteal",
                        "description":"Concentre toutes les attaques ennemies sur lui jusqu'à son prochain tour, gagne 30% de degats encaisses.",
                        "cost":{"pa":4,"mitigation":1}
                    },
                    "Caber":{
                        "nom":"Caber",
                        "description":"lance sa massue sur un ennemi, 50% de chances de l'étourdir et 15% de chances que l'attaque se transmette à un autre ennemi",
                        "cost":{
                            "pa":3
                    }
                },
                "Fureur de Fachan":{
                    "nom":"Fureur de Fachan",
                    "description":"Diminue de 20% les dégâts pour chaque stack de mitigation possédé",
                    "cost":{
                        "pa":0
                    }
                },
                "Tignasse":{
                    "nom":"Tignasse",
                    "description":"Protège toute l'equipe avec sa chevelure. 15% de dommages en moins,
                    "cost":{"pa":3}},
                "Stalin":{
                    "nom":"Stalin",
                    "description":"Deviens l'Homme de Fer et encaisse tous les dégâts physiques pendant les trois prochains tours. Gagne un stack de mitigation",
                    "cost":{"pa":4}
                },
                "Où sont mes pieds":{
                    "nom":"Où sont mes pieds",
                    "description":"Cherche sa deuxième jambe, devient incapable d'attaquer mais récupère 50% de ses pv",
                    "cost":{"pa":4}
                }
            }
        }
