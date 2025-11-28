class File:

    def __init__ (self, content = []):
        self.contenu = content

    def defiler (self):
        return self.contenu.pop(0)
    
    def empiler (self, valeur):
        self.contenu.append(valeur)

    