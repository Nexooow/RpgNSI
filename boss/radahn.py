from random import choice, randint
from time import time

import pygame

from base.action import Action
from lib.render import text_render_centered_up, text_render_centered
from sprites.Explosion import Explosion
from sprites.Meteor import Meteor
from sprites.demiurge import Fighter


def display_frames(image, frame_width, frame_height):
    frames = []
    sheet_width = image.get_width()
    num_frames = sheet_width // frame_width
    for i in range(num_frames):
        frame = image.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames


def draw_health(screen, health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, (255, 255, 255), (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, (255, 0, 0), (x, y, 400, 30))
    pygame.draw.rect(screen, (0, 255, 255), (x, y, 400 * ratio, 30))


background = pygame.image.load("./assets/sprites/radahn_fightzone.jpg")
half_radahn = pygame.image.load("./assets/sprites/radahn.png")
radahn_frames = display_frames(half_radahn, 1422 // 2, 1600 // 3)
player_sheet = pygame.image.load("./assets/sprites/warrior.png")
player = Fighter(500, 480, [162, 1, [72, 56]], player_sheet, [10, 8, 1, 7, 7, 3, 7], {1: [4], 2: [2]},
                 hitbox_height=162)


class Radahn(Action):
    
    def __init__(self, jeu, _):
        super().__init__(jeu)
        self.start_time = None
        self.desactive_ui = True
        self.utilise_musique = True
        self.utilise_musique = True
        self.radahn_frame_index = 0
        self.explosion_group = pygame.sprite.Group()
        self.meteors = []

    def executer(self):
        self.start_time = time()
        self.radahn_frame_index = 0
        self.jeu.jouer_musique("survive", loop=False)
        self.jeu.jouer_musique("survive", loop=False)

    def update(self, events):
        pass

    def draw(self):
        this = randint(1, 275)
        if len(self.meteors) < 10 and this <= 10:
            if this > 3:
                self.meteors.append(Meteor((randint(25, 910), -25)))
            else:
                border = choice([25, 910])
                self.meteors.append(Meteor((border, randint(-25, 150))))
        self.jeu.fond.blit(background, (0, 0))
        draw_health(self.jeu.fond, player.health, 20, 600)
        player.move(1000, 700, self.jeu.fond, target=None)
        self.jeu.fond.blit(radahn_frames[self.radahn_frame_index], (150, 40))
        self.radahn_frame_index = (self.radahn_frame_index + 1) % len(radahn_frames)
        for meteor in self.meteors:
            meteor.deplace(player)
            meteor.frame_index = (meteor.frame_index + 1) % len(meteor.frames)
            meteor.collision(player)
            pygame.draw.circle(self.jeu.fond, (255, 0, 0), meteor.rect.center, int(meteor.radiuspx), 1)
            if meteor.rect.bottom >= 500:
                self.meteors.remove(meteor)
                explosion = Explosion(
                    meteor.rect.center[0], meteor.rect.center[1], meteor.size
                )
                self.explosion_group.add(explosion)
            else:
                self.jeu.fond.blit(meteor.frame, meteor.rect)
        player.update()
        player.draw(self.jeu.fond)


        self.explosion_group.draw(self.jeu.fond)
        self.explosion_group.update()

        temps = 195 - round(time() - self.start_time)
        texte = (
            "Time: " + str(195 - round(time() - self.start_time))
            if 195 - round(time() - self.start_time) > 0
            else ""
        )
        if player.health > 0 and temps > 0:
            text_render_centered_up(
                self.jeu.ui_surface, "Survive", "bold", color=(255, 0, 0), pos=(500, 100)
            )
            text_render_centered_up(
                self.jeu.ui_surface,
                texte,
                "bold",
                color=(255, 0, 0),
                pos=(500, 150),
            )
        if player.health <= 0:
            text_render_centered(self.jeu.ui_surface, "GIT GUD", "extrabold", color=(255, 0, 0), pos=(500, 350))
            # Téléporter l'équipe à l'auberge et soigner
            self.jeu.region = "Auberge"
            self.jeu.lieu = self.jeu.regions["Auberge"].entree
            self.jeu.equipe.soigner_complet()
            self.jeu.actions.contenu = []
            self.complete = True
            # Téléporter l'équipe à l'auberge et soigner
            self.jeu.region = "Auberge"
            self.jeu.lieu = self.jeu.regions["Auberge"].entree
            self.jeu.equipe.soigner_complet()
            self.jeu.actions.contenu = []
            self.complete = True
        if 195 - round(time() - self.start_time) == 0:
            pygame.mixer.music.stop()
            text_render_centered(self.jeu.ui_surface, "Great Finger Obtained", "bold", color=(255, 215, 0),
                                 pos=(500, 350))
            self.jeu.variables_jeu['radahn_killed'] = True
            self.complete = True