class Menu:
    
    def __init__ (self, jeu):
        self.jeu = jeu
        pass
        
    def ouvrir (self):
        pass

    def fermer (self):
        self.jeu.fermer_menu()
        
    def update (self, events):
        pass
        
    def draw (self):
        pass