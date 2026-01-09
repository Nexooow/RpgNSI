import pygame


class Action:
    """
    Classe représentant une action dans la file de la classe Jeu.
    Peut-être dessinée sur la fenêtre pygame (via Action#draw), et mise à jour selon les événements pygame (via Action#update).
    """

    def __init__(self, jeu, data=None):
        if data is None:
            data = {}
        self.complete = False
        self.jeu = jeu
        self.data = data
        
        self.desactive_ui = False
        self.utilise_fond = False # si oui, le fond de la région sera arrêté pendant l'action
        self.utilise_musique = False  # si oui, le theme de la région sera arrêté pendant l'action

    def __str__(self):
        """
        Utiliser pour debug
        """
        return f"{self.__class__.__name__} ({str(self.data)})"

    def draw(self):
        """
        Dessine sur la fenêtre pygame.
        :return: None
        """
        pass

    def update(self, events: list):
        """
        Met à jour l'action selon les événements pygame
        :param events: événéments pygames
        :return: None
        """
        pass

    def executer(self):
        """
        Exécuté lorsque l'action démarre
        :return: None
        """
        self.complete = False

    def get_complete(self):
        """
        Renvoie le statut de l'action
        :return: si l'action est complète ou non
        """
        return self.complete
