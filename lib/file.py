class File:

    def __init__(self, content=None):
        if content is None:
            content = []
        self.contenu = content

    def __repr__(self):
        return str(self.contenu)

    def defiler(self):
        return self.contenu.pop(0)

    def enfiler(self, valeur):
        self.contenu.append(valeur)

    def inserer(self, liste: list):
        """
        Force l'insertion au début de la file
        :param liste: liste à insérer
        :return: None
        """
        self.contenu = liste + self.contenu

    def sommet(self):
        return self.contenu[0]

    def est_vide(self):
        return len(self.contenu) == 0
