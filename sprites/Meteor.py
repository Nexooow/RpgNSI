import math
from random import randint
import pygame


class Meteor:
    def __init__(self, center, frame_index=0, object_density=3000.0):
        self.image = pygame.image.load(
            "./assets/sprites/meteor.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.point_of_fall = center
        self.speed = randint(1, 3)
        self.gravity = 0.1
        self.x_speed = (
            randint(2, 10)
            if center[0] == 25
            else randint(-10, -2)
            if center[0] == 910
            else randint(-10, 10)
        )
        self.size = randint(1, 6) * 0.1
        self.meteor_density = object_density
        self.air_density = 1.225
        self.Cd = 1.0
        self.mps = 0.02  # pour la conversion de metres en pixels
        self.fps = 60.0
        self.dt = 1.0 / 60.0
        self.g = 9.81
        self.frames = self.load_frames()
        self.frame = self.frames[0]
        self.frame_index = frame_index
        self.radius = self.frames[0].get_width() * self.mps / 2.0
        self.radiuspx = self.frames[0].get_width() // 3.0
        self.surface = math.pi * self.radius**2
        self.mass = (
            self.meteor_density * (4.0 / 3.0) * math.pi * (self.radius**3)
        )  # on assume que l'objet est une sphère
        self.term_v = math.sqrt(
            (2 * self.mass * self.g) / (self.air_density * self.Cd * self.surface)
        )
        self.has_hit = False
        self.mask=pygame.mask.from_surface(self.frame)

    def deplace(self, target):
        v = self.speed
        traine = 0.5 * self.air_density * self.Cd * self.surface * v**2 / self.mass
        a = self.g - traine
        self.speed += a * self.dt
        y_velocity = self.speed / self.mps * self.dt
        self.speed = min(self.speed, 30)
        self.speed += self.gravity
        self.rect = self.rect.move(self.x_speed, int(y_velocity))
        angle = math.atan(self.x_speed / y_velocity)
        current_frame = self.frames[self.frame_index]
        self.frame = pygame.transform.rotate(
            current_frame, angle * 180 / math.pi)
        centre = self.rect.center
        self.rect = self.frame.get_rect(center=centre)
        self.mask = pygame.mask.from_surface(self.frame)
        offset_x=target.img_pos[0] - self.rect.left
        offset_y=target.img_pos[1] - self.rect.top
        overlap=self.mask.overlap(target.mask,(offset_x,offset_y))
        if overlap and not self.has_hit:
            target.health-=self.impact_force()
            self.has_hit=True

    def impact_force(self):
        vx = self.x_speed
        vy = self.speed / self.mps
        velocity = math.sqrt(vx**2+vy**2)
        f = int(0.5*self.mass*(velocity**2)/4000000)
        print(f)
        return f

    def collision(self, target):
        """
        x = self.rect.centerx-target.rect.centerx
        y = self.rect.centery-target.rect.centery+10
        distance = math.sqrt(x**2+y**2)
        if distance <= self.radiuspx + target.radiuspx and not self.has_hit:
            target.health -= self.impact_force()
            self.has_hit = True
        """
        offset=(target.rect.left - self.rect.left, target.rect.top - self.rect.top)
        overlap=self.mask.overlap(target.mask,offset)
        if overlap and not self.has_hit:
            target.health-=self.impact_force()
            self.has_hit=True
    def load_frames(self, frame_width=448, frame_height=448):
        frames = []
        sheet_width = self.image.get_width()
        # sheet_height = self.image.get_height()
        num_frames = sheet_width // frame_width
        for i in range(num_frames):
            frame = self.image.subsurface(
                (i * frame_width, 0, frame_width, frame_height)
            )
            scale_w = int(frame_width * self.size)
            scale_h = int(frame_height * self.size)
            frame = pygame.transform.scale(frame, (scale_w, scale_h))

            frames.append(frame)
        self.rect = frames[0].get_rect(center=self.rect.center)
        return frames
