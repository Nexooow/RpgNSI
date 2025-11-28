import pygame
import json
import os

import Jeu

saves = os.listdir("./saves")
print(saves)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

def show_main_menu():
    screen.fill("white")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    # TODO: game render
    show_main_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()