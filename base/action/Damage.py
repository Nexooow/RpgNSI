from .Action import Action

class Damage(Action):
    """
    Inflige des dégâts au joueur.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)

    def executer(self):
        super().executer()
        degats = self.data.get("degats", 0)
        if "personnage" in self.data and self.jeu.equipe.personnage_debloque(self.data["personnage"]):
            self.jeu.equipe.get_personnage(self.data["personnage"]).infliger(degats)
        else:
            self.jeu.equipe.infliger(degats)
        self.complete = True
