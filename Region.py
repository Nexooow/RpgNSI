from lib.graph import Graph

class Region:
    
    def __init__(self, jeu, nom, action_entree = None, action_sortie = None, image="background.webp"):
        self.jeu = jeu
        self.nom = nom
        self.carte = Graph(image=image)
        self.lieux = {}
        self.entree = None
        self.position = self.jeu.carte.pos[self.nom]
        self.action_entree = action_entree
        self.action_sortie = action_sortie
        
    def afficher (self):
        self.carte.affichage(self.jeu.ui_surface)
        
    def entrer (self):
        if self.nom not in self.jeu.lieux_visite:
            if self.action_entree:
                self.jeu.executer_sequence(self.action_entree)

    def sortir (self):
        if self.nom in self.jeu.lieux_visite:
            self.jeu.lieux_visite.add(self.nom)
            if self.action_sortie:
                self.jeu.executer_sequence(self.action_sortie)
