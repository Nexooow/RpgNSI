import JSONLoader

class Jeu:

    def __init__ (self, json: dict):
        self.loader = JSONLoader(self)
        # TODO: restaurer les attributs du json dans la classe (si fourni)