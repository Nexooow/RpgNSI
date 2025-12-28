class Equipe:

    def __init__ (self):

        self.argent = 100
        self.personnages = []
        self.inventaire = {}

    def restaurer (self, json):
        self.argent = json["argent"]
        self.inventaire = json["inventaire"]
        self.personnages = json["personnages"] # TODO: charger les personnages selon le json indiqué

