
class Arbre:

    def __init__ (self, data):
        self.data = data
        self.right = None
        self.left = None

    def get_data (self):
        return self.data

    def get_right (self):
        return self.right

    def get_left (self):
        return self.left

    def set_right (self, arbre):
        self.right = arbre

    def set_left (self, arbre):
        self.left = arbre

def afficher_arbre (arbre, surface, competences_debloques):
    # TODO: dessiner l'arbre sur la fenêtre
    print(arbre.get_data())