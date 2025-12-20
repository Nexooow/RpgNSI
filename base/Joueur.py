class Joueur:

    def __init__ (self, jeu, json):
        self.jeu = jeu
        if json is not None:
            for key, valeur in json.items():
                if key == "jeu":
                    continue
                else:
                    setattr(self, key, valeur)
        else:
            self.vie_max = 100
            self.vie = 100

            self.force = 10
            self.vitesse = 10

            self.chance = 25

            self.inventaire = {}
            self.equipment = {
                "main": None,
                "main_secondaire": None,
                "tete": None,
                "torse": None,
                "jambes": None,
                "pieds": None
            }
        
    def sauvegarder (self):
        return {
            "vie_max": self.vie_max,
            "vie": self.vie,
            "force": self.force,
            "vitesse": self.vitesse,
            "chance": self.chance,
            "inventaire": self.inventaire,
            "equipment": self.equipment
        }
    
    def infliger (self, degats):
        self.vie -= degats
        
    def soigner (self, points):
        self.vie += points
        if self.vie > self.vie_max:
            self.vie = self.vie_max
            
    def ajouter_objet (self, objet, quantite = 1):
        if objet in self.inventaire:
            self.inventaire[objet] += quantite
        else:
            self.inventaire[objet] = quantite
            
    def retirer_objet (self, objet, quantite = 1):
        if objet in self.inventaire:
            self.inventaire[objet] -= quantite
            if self.inventaire[objet] <= 0:
                del self.inventaire[objet] # retire la clé du dictionnaire
        