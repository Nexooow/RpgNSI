import uuid
import pygame
import json
import os
from lib.render import text_render_centered

from Jeu import Jeu

try:
    saves = os.listdir("./saves")
except FileNotFoundError:
    saves = []

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

running = True
jeu = None

def show_main_menu():
    global running, jeu
    
    text_render_centered(screen, "Coucou", "extrabold", pos=(1280/2, 150))
    
    text_render_centered(screen, "Créer une partie", "regular", pos=(1280/2, 325))
    text_render_centered(screen, "Charger une partie", "regular", color = (0, 0, 0) if len(saves) > 0 else (155, 155, 155), pos=(1280/2, 375))
    text_render_centered(screen, "Paramètres", "regular", pos=(1280/2, 425))
    text_render_centered(screen, "Quitter", "regular", pos=(1280/2, 475))
    
    # lorsqu'un bouton est survolé, souligner le texte
    mouse_pos = pygame.mouse.get_pos()
    if 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 325 - 25 <= mouse_pos[1] <= 325 + 25:
        text_render_centered(screen, "Créer une partie", "regular", color=(0, 0, 0), pos=(1280/2, 325), underline=True)
    elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 375 - 25 <= mouse_pos[1] <= 375 + 25:
        if len(saves) > 0:
            text_render_centered(screen, "Charger une partie", "regular", color=(0, 0, 0), pos=(1280/2, 375), underline=True)
    elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 425 - 25 <= mouse_pos[1] <= 425 + 25:
        text_render_centered(screen, "Paramètres", "regular", pos=(1280/2, 425), underline=True)
    elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 475 - 25 <= mouse_pos[1] <= 475 + 25:
        text_render_centered(screen, "Quitter", "regular", pos=(1280/2, 475), underline=True)
        
    # lorsque l'utilisateur clique sur un bouton, executer l'action liée
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 325 - 25 <= mouse_pos[1] <= 325 + 25:
                # "Créer une partie"
                jeu = Jeu(str(uuid.uuid4()))
            elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 375 - 25 <= mouse_pos[1] <= 375 + 25:
                # "Charger une partie"
                if len(saves) > 0:
                    pass
            elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 425 - 25 <= mouse_pos[1] <= 425 + 25:
                # "Paramètres"
                pass
            elif 1280/2 - 100 <= mouse_pos[0] <= 1280/2 + 100 and 475 - 25 <= mouse_pos[1] <= 475 + 25:
                # "Quitter"
                running = False
    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    
    if jeu is None:
        show_main_menu()
    else:
        jeu.scene(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()