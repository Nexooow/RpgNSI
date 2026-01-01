print("⚠️ La console ne sert qu'à déboguer le jeu.")

import pygame

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Game Name")

screen = pygame.display.set_mode((1000, 700))

from Jeu import Jeu

if __name__ == "__main__":

    jeu = Jeu()

    while jeu.running:

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                jeu.quitter()

        jeu.gerer_evenement(events)
        jeu.executer()

        screen.fill((0, 0, 0))
        jeu.fond.fill((0, 0, 0, 0))
        jeu.ui_surface.fill((0, 0, 0, 0))
        jeu.filter_surface.fill((0, 0, 0, 0))

        jeu.scene()

        screen.blit(jeu.fond, (0, 0))
        screen.blit(jeu.ui_surface, (0, 0))
        screen.blit(jeu.filter_surface, (0, 0))

        pygame.display.flip()
        jeu.clock.tick(60)

    pygame.quit()
