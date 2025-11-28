import pygame

class Action:
    
    def __init__ (self, json):
        self.complete = False
        self.json = json
        
    def draw (self, screen):
        pass
        
    def update (self, events):
        pass
        
    def executer (self):
        pass

class Dialogue (Action):
    
    def __init__ (self, json):
        super().__init__(json)
        
    def draw (self, screen):
        pass
        
    def update (self, events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.complete = True
        
    def executer (self):
        pass
