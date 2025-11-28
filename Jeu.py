import JSONLoader
from lib.file import File

class Jeu:

    def __init__ (self, json: dict):
        self.loader = JSONLoader(self)
        self.scenes = File()
        # TODO: restaurer les attributs du json dans la classe (si fourni)

    def show (self):
        pass