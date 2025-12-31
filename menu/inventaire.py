import pygame
from menu.Menu import Menu

from lib.render import text_render_centered_left, text_render_centered


class Inventaire(Menu):

    def __init__(self, jeu):
        super().__init__(jeu)
        self.selection = 0

    def update(self, events):
        items_ids = list(self.jeu.equipe.inventaire.keys())
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if items_ids:
                        self.selection = (self.selection + 1) % len(items_ids)
                elif event.key == pygame.K_UP:
                    if items_ids:
                        self.selection = (self.selection - 1) % len(items_ids)
                elif event.key == pygame.K_SPACE:
                    if items_ids:
                        self.utiliser_item(items_ids[self.selection])
                elif event.key == pygame.K_ESCAPE:
                    self.fermer()

    def ajouter_item(self, item_id, quantite=1):
        if item_id in self.jeu.joueur.inventaire:
            self.jeu.joueur.inventaire[item_id] += quantite
        else:
            self.jeu.joueur.inventaire[item_id] = quantite

    def utiliser_item(self, item_id):
        item_data = self.jeu.items.get(item_id)
        if not item_data:
            return

        # TODO: utilisation item (+ selon type: consommable, armure, arme...)

    def draw(self):

        text_render_centered(self.jeu.ui_surface, "INVENTAIRE", "bold", color=(255, 255, 255),
                             pos=(self.jeu.WIDTH // 2, 50), size=40)

        items_ids = list(self.jeu.equipe.inventaire.keys())

        start_x = 50
        start_y = 120

        for i, item_id in enumerate(items_ids):
            item_data = self.jeu.items.get(item_id, {"nom": item_id})
            quantite = self.jeu.equipe.inventaire[item_id]
            couleur = (255, 255, 255) if i != self.selection else (255, 200, 100)
            prefixe = "> " if i == self.selection else "  "

            text_render_centered_left(
                self.jeu.ui_surface,
                f"{prefixe}{item_data['nom']} (x{quantite})",
                "regular",
                color=couleur,
                pos=(start_x, start_y + i * 40),
                size=24
            )

        if items_ids and self.selection < len(items_ids):

            item_id = items_ids[self.selection]
            item_data = self.jeu.items.get(item_id)

            if item_data:
                detail_x = 500
                detail_y = 120

                text_render_centered_left(self.jeu.ui_surface, item_data["nom"], "bold", color=(255, 200, 100),
                                          pos=(detail_x, detail_y), size=32)
                text_render_centered_left(self.jeu.ui_surface, f"Type: {item_data.get('type', 'Inconnu')}", "imitalic",
                                          color=(200, 200, 200), pos=(detail_x, detail_y + 40), size=20)

                desc = item_data.get("description", "")
                text_render_centered_left(self.jeu.ui_surface, desc, "regular", color=(255, 255, 255),
                                          pos=(detail_x, detail_y + 80), size=22)

                text_render_centered_left(self.jeu.ui_surface, "[ESPACE] Utiliser / [ECHAP] Retour", "regular",
                                          color=(150, 150, 150), pos=(detail_x, 600), size=18)

        elif not items_ids:

            text_render_centered(self.jeu.ui_surface, "L'inventaire est vide", "imitalic", color=(150, 150, 150),
                                 pos=(self.jeu.WIDTH // 2, self.jeu.HEIGHT // 2), size=30)
