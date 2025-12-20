import pygame
from base.Action import Action

from sprites.demiurge import Fighter

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
warrior_size = 162
warrior_scale = 4
warrior_offset = [72, 56]
warrior_data = [warrior_size, warrior_scale, warrior_offset]
demiurge_size = 250
demiurge_scale = 3
demiurge_offset = [112, 107]
demiurge_data = [demiurge_size, demiurge_scale, demiurge_offset]
warrior_animation_steps = [10, 8, 1, 7, 7, 3, 7]
demiurge_animation_steps = [8, 8, 1, 8, 8, 3, 7]


class StreetFighter (Action):

    def __init__(self, jeu):
        self.jeu = jeu
        self.desactive_ui = True
        warrior_sheet = pygame.image.load(
            "./assets/sprites/warrior.png").convert_alpha()
        demiurge_sheet = pygame.image.load(
            "./assets/sprites/wizard.png").convert_alpha()
        self.demiurge = Fighter(200, 310, demiurge_data, demiurge_sheet,
                                demiurge_animation_steps)
        self.player = Fighter(700, 310, warrior_data, warrior_sheet,
                              warrior_animation_steps)

    def draw_bg(self):
        background = pygame.image.load("images.jpg").convert_alpha()
        background = pygame.transform.scale(background, 100)
        self.jeu.fond.blit(background, (0, 0))

    def draw_health(self, health, x, y):
        ratio = health/100
        pygame.draw.rect(self.jeu.ui_surface, WHITE, (x-2, y-2, 404, 34))
        pygame.draw.rect(self.jeu.ui_surface, RED, (x, y, 400, 30))
        pygame.draw.rect(self.jeu.ui_surface, YELLOW, (x, y, 400*ratio, 30))

    def draw(self):
        self.draw_bg()
        self.draw_health(self.player.health, 20, 20)
        self.draw_health(self.demiurge.health, 500, 20)
        self.demiurge.draw(self.jeu.fond)

    def update (self, events):
        self.player.move(1000, 700, self.jeu.fond, self.demiurge)
        self.demiurge.move(1000, 700, self.jeu.fond, self.player, False)
        self.demiurge.ai_behavior(self.jeu.fond, self.player)
