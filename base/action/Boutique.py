import pygame
from .Action import Action
from lib.render import text_render_centered_left, text_render_centered


class Boutique(Action):
    """
    Action qui représente la boutique directement (sans passer par un menu).
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True
        self.items = data.get("items", [])
        self.shop_id = data.get("shop_id", "default_shop")
        self.selection = 0

        # ajouter les stocks aux variables jeu (si non présentes)
        for item in self.items:
            stock_key = f"shop:{self.shop_id}:{item['id']}:stock"
            item["stock_key"] = stock_key
            if stock_key not in self.jeu.variables_jeu:
                self.jeu.variables_jeu[stock_key] = item.get("stock", 99)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if self.items:
                        self.selection = (self.selection + 1) % len(self.items)
                elif event.key == pygame.K_UP:
                    if self.items:
                        self.selection = (self.selection - 1) % len(self.items)
                elif event.key == pygame.K_SPACE:
                    if self.items:
                        self.acheter_item(self.items[self.selection])
                elif event.key == pygame.K_ESCAPE:
                    self.complete = True

    def acheter_item(self, item_info):
        item_id = item_info["id"]
        prix = item_info["prix"]
        stock_key = item_info.get("stock_key")

        # verifier argent
        if self.jeu.equipe.argent >= prix:
            # verifier stock
            if stock_key:
                stock = self.jeu.variables_jeu.get(stock_key, 0)
                if stock <= 0:
                    print("Plus de stock !")
                    return
                self.jeu.variables_jeu[stock_key] -= 1

            # ajout item
            self.jeu.equipe.argent -= prix
            self.jeu.equipe.ajouter_item(item_id, 1)
            print(f"Acheté {item_id} pour {prix}€")
        else:
            print("Pas assez d'argent !")

    def draw(self):

        overlay = pygame.Surface((self.jeu.WIDTH, self.jeu.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.jeu.ui_surface.blit(overlay, (0, 0))

        text_render_centered(self.jeu.ui_surface, "BOUTIQUE", "bold", color=(255, 255, 255),
                             pos=(self.jeu.WIDTH // 2, 50), size=40)

        text_render_centered(self.jeu.ui_surface, f"Votre argent: {self.jeu.equipe.argent} €", "regular",
                             color=(255, 215, 100),
                             pos=(self.jeu.WIDTH // 2, 90), size=24)

        start_x = 50
        start_y = 150

        for i, item_info in enumerate(self.items):
            item_id = item_info["id"]
            prix = item_info["prix"]
            stock_key = item_info.get("stock_key")

            item_data = self.jeu.loader.items.get(item_id, {"nom": item_id})
            stock = self.jeu.variables_jeu.get(stock_key, "∞") if stock_key else "∞"

            couleur = (255, 255, 255) if i != self.selection else (255, 200, 100)
            if stock != "∞" and stock <= 0:
                couleur = (100, 100, 100)

            prefixe = "> " if i == self.selection else "  "

            text_render_centered_left(
                self.jeu.ui_surface,
                f"{prefixe}{item_data['nom']} - {prix}€ (Stock: {stock})",
                "regular",
                color=couleur,
                pos=(start_x, start_y + i * 40),
                size=24
            )

        if self.items and self.selection < len(self.items):
            item_info = self.items[self.selection]
            item_data = self.jeu.loader.items.get(item_info["id"])

            if item_data:
                detail_x = 550
                detail_y = 150

                text_render_centered_left(self.jeu.ui_surface, item_data["nom"], "bold", color=(255, 200, 100),
                                          pos=(detail_x, detail_y), size=32)

                desc = item_data.get("description", "")
                # Simple line wrap (très basique)
                words = desc.split(' ')
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) < 30:
                        current_line += word + " "
                    else:
                        lines.append(current_line)
                        current_line = word + " "
                lines.append(current_line)

                for j, line in enumerate(lines):
                    text_render_centered_left(self.jeu.ui_surface, line, "regular", color=(220, 220, 220),
                                              pos=(detail_x, detail_y + 60 + j * 25), size=20)

                text_render_centered_left(self.jeu.ui_surface, "[ESPACE] Acheter / [ECHAP] Quitter", "regular",
                                          color=(150, 150, 150), pos=(detail_x, 600), size=18)

    def executer(self):
        super().executer()
