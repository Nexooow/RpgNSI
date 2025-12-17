from random import choice, randint
from time import time

import pygame

from Action import Action
from lib.render import text_render_centered_up
from sprites.Explosion import Explosion
from sprites.Meteor import Meteor


def display_frames(image, frame_width, frame_height):
    frames = []
    sheet_width = image.get_width()
    num_frames = sheet_width // frame_width
    for i in range(num_frames):
        frame = image.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames


background = pygame.image.load("./assets/sprites/radahn_fightzone.jpg")
half_radahn = pygame.image.load("./assets/sprites/radahn.png")
radahn_frames = display_frames(half_radahn, 1422 // 2, 1600 // 3)


class Radahn(Action):
    def __init__(self, jeu):
        super().__init__(jeu)
        self.desactive_ui = True
        self.radahn_frame_index = 0
        self.explosion_group = pygame.sprite.Group()
        self.meteors = []

    def executer(self):
        self.start_time = time()
        self.radahn_frame_index = 0
        pygame.mixer.music.set_volume(100)
        pygame.mixer.music.load("./assets/music/survive.mp4")
        pygame.mixer.music.play()

    def update(self, events):
        pass

    def draw(self):
        this = randint(1, 200)
        if len(self.meteors) < 10 and this <= 10:
            if this > 3:
                self.meteors.append(Meteor((randint(25, 910), -25)))
            else:
                border = choice([25, 910])
                self.meteors.append(Meteor((border, randint(-25, 150))))
        self.jeu.fond.blit(background, (0, 0))

        self.jeu.fond.blit(radahn_frames[self.radahn_frame_index], (150, 40))
        self.radahn_frame_index = (self.radahn_frame_index + 1) % len(radahn_frames)
        for meteor in self.meteors:
            meteor.deplace()
            meteor.frame_index = (meteor.frame_index + 1) % len(meteor.frames)
            if meteor.rect.bottom >= 480:
                self.meteors.remove(meteor)
                explosion = Explosion(
                    meteor.rect.center[0], meteor.rect.center[1], meteor.size
                )
                self.explosion_group.add(explosion)
            else:
                self.jeu.fond.blit(meteor.frame, meteor.rect)
        self.explosion_group.draw(self.jeu.fond)
        self.explosion_group.update()
        text_render_centered_up(
            self.jeu.ui_surface, "Survive", "bold", color=(255, 0, 0), pos=(500, 100)
        )
        texte = (
            "Time: " + str(195 - round(time() - self.start_time))
            if 195 - round(time() - self.start_time) > 0
            else ""
        )
        text_render_centered_up(
            self.jeu.ui_surface,
            texte,
            "bold",
            color=(255, 0, 0),
            pos=(500, 150),
        )
        if 195 - round(time() - self.start_time) == 0:
            pygame.mixer.music.stop()
