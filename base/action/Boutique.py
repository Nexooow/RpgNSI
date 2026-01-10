import pygame
from .Action import Action
from lib.render import text_render_centered_left, text_render_centered
from lib.sounds import son_selection


class Boutique(Action):
    """
    Action qui représente la boutique.
    """

    def __init__(self, jeu, data):
        super().__init__(jeu, data)
        self.desactive_ui = True
        self.items = data.get("items", [])
        self.shop_id = data.get("shop_id", "default_shop")
        self.selection = 0
        self.mode = "achat"  # "achat"/"vente"

        # ajouter les stocks aux variables jeu (si non présentes)
        for item in self.items:
            stock_key = f"shop:{self.shop_id}:{item['id']}:stock"
            item["stock_key"] = stock_key
            if stock_key not in self.jeu.variables_jeu:
                self.jeu.variables_jeu[stock_key] = item.get("stock", 99)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.mode = "vente" if self.mode == "achat" else "achat"
                    self.selection = 0
                elif event.key == pygame.K_DOWN:
                    items = self.get_items()
                    if items:
                        son_selection.play()
                        self.selection = (self.selection + 1) % len(items)
                elif event.key == pygame.K_UP:
                    items = self.get_items()
                    if items:
                        son_selection.play()
                        self.selection = (self.selection - 1) % len(items)
                elif event.key == pygame.K_SPACE:
                    items = self.get_items()
                    if items:
                        if self.mode == "achat":
                            self.acheter_item(items[self.selection])
                        elif self.mode == "vente":
                            self.vendre_item(items[self.selection])
                elif event.key == pygame.K_ESCAPE:
                    self.complete = True

    def get_items(self):
        if self.mode == "achat":
            return self.items
        elif self.mode == "vente":
            return [item for item in self.jeu.equipe.inventaire if "valeur" in self.jeu.loader.items.get(item, {})]

    def vendre_item(self, item_id):
        item_data = self.jeu.loader.items.get(item_id, {})
        valeur = item_data.get("valeur", 0)

        if valeur > 0:
            self.jeu.equipe.argent += valeur
            self.jeu.equipe.retirer_item(item_id, 1)
            print(f"Vendu {item_data.get('nom', item_id)} pour {valeur}€")
        else:
            print("Cet item ne peut pas être vendu")

    def acheter_item(self, item):
        item_id = item["id"]
        prix = item["prix"]
        stock_key = item.get("stock_key")

        if self.jeu.equipe.argent >= prix:
            if stock_key and self.jeu.variables_jeu.get(stock_key, 0) > 0:
                self.jeu.variables_jeu[stock_key] -= 1
            self.jeu.equipe.argent -= prix
            self.jeu.equipe.ajouter_item(item_id, 1)
            print(f"Acheté {item_id} pour {prix}€")
        else:
            print("Pas assez d'argent pour acheter cet item")

    def draw(self):

        overlay = pygame.Surface((self.jeu.WIDTH, self.jeu.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.jeu.ui_surface.blit(overlay, (0, 0))

        titre = "BOUTIQUE - ACHAT" if self.mode == "achat" else "BOUTIQUE - VENTE"
        text_render_centered(self.jeu.ui_surface, titre, "bold", color=(255, 255, 255),
                             pos=(self.jeu.WIDTH // 2, 50), size=40)

        text_render_centered(self.jeu.ui_surface, f"Votre argent: {self.jeu.equipe.argent} €", "regular",
                             color=(255, 215, 100), pos=(self.jeu.WIDTH // 2, 90), size=24)

        start_x = 50
        start_y = 150

        items = self.get_items()
        for i, item_info in enumerate(items):
            if self.mode == "achat":
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
            elif self.mode == "vente":
                item_data = self.jeu.loader.items.get(item_info, {"nom": item_info})
                valeur = item_data.get("valeur", 0)
                couleur = (255, 255, 255) if i != self.selection else (255, 200, 100)
                prefixe = "> " if i == self.selection else "  "
                text_render_centered_left(
                    self.jeu.ui_surface,
                    f"{prefixe}{item_data['nom']} - {valeur}€",
                    "regular",
                    color=couleur,
                    pos=(start_x, start_y + i * 40),
                    size=24
                )

        text_render_centered_left(self.jeu.ui_surface, "[TAB] Changer mode / [ESPACE] Confirmer / [ECHAP] Quitter",
                                  "imregular", color=(150, 150, 150), pos=(start_x, 600), size=18)

    def executer(self):
        super().executer()
