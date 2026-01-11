from base.Personnage import Personnage, Barman, Fachan, Vous
import typing

classes_personnages = {
    "Barman": Barman,
    "Vous": Vous,
    "Fachan": Fachan
}


class Equipe:

    def __init__(self, jeu):
        self.jeu = jeu
        self.argent = 100
        self.chance = 10
        self.personnages: list[Personnage] = []  # Liste des personnages dans l'équipe (c.-à-d. débloqués)
        self.inventaire = {}

    def get_personnage(self, nom) -> typing.Optional[Personnage]:
        for personnage in self.personnages:
            if personnage.nom == nom:
                return personnage
        return None

    def personnage_debloque(self, nom) -> bool:
        personnage = self.get_personnage(nom)
        return personnage is not None

    def ajouter_personnage(self, personnage):
        self.personnages.append(personnage)

    def equiper_personnage(self, nom, item_id):
        if item_id in self.inventaire:
            personnage = self.get_personnage(nom)
            if personnage:
                personnage.equiper(item_id)

    def ajouter_item(self, item_id, quantite=1):
        if item_id in self.inventaire:
            self.inventaire[item_id] += quantite
        else:
            self.inventaire[item_id] = quantite

    def retirer_item(self, item_id, quantite=None):
        if item_id in self.inventaire:
            if quantite is None:
                del self.inventaire[item_id]
            else:
                self.inventaire[item_id] -= quantite
                if self.inventaire[item_id] <= 0:
                    del self.inventaire[item_id]

    def ajouter_xp(self, xp):
        for personnage in self.personnages:
            personnage.xp += xp

    def restaurer(self, json):
        self.argent = json["argent"]
        self.chance = json["chance"]
        self.inventaire = json["inventaire"]
        for personnage in json["personnages"]:
            perso = classes_personnages[personnage["nom"]]
            self.ajouter_personnage(
                perso(self, personnage)
            )

    def sauvegarder(self):
        return {
            "argent": self.argent,
            "chance": self.chance,
            "inventaire": self.inventaire,
            "personnages": [
                personnage.sauvegarder() for personnage in self.personnages
            ]
        }

    def infliger(self, degats):
        for personnage in self.personnages:
            personnage.infliger(degats)

    def soigner(self, points):
        for personnage in self.personnages:
            personnage.soigner(points)

    def soigner_complet(self):
        """Soigne tous les personnages à leur vie maximum."""
        for personnage in self.personnages:
            personnage.attributs["vie"] = personnage.attributs["vie_max"]
            personnage.alive = True

    def tous_morts(self):
        """Vérifie si tous les personnages sont morts."""
        for personnage in self.personnages:
            if personnage.attributs["vie"] > 0:
                return False
        return True
