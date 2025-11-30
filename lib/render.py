import pygame


def font_render (text, font, color=(0, 0, 0), size=None):
    if font == "extrabold":
        font = pygame.font.Font("./assets/fonts/CinzelDecorative-Black.ttf", size or 56)
    elif font == "bold":
        font = pygame.font.Font("./assets/fonts/CinzelDecorative-Bold.ttf", size or 48)
    else:
        font = pygame.font.Font("./assets/fonts/CinzelDecorative-Regular.ttf", size or 36)
    return font.render(text, True, color)
    
def text_render_centered(surface, text, font, color=(0, 0, 0), pos=(0, 0), underline = False, size = None):
    text_surface = font_render(text, font, color, size)
    if underline:
        underline_color = (color[0], color[1], color[2], 120)
        text_largueur, text_hauteur = text_surface.get_size()
        underline_start = (pos[0] - text_largueur / 2, pos[1] + text_hauteur / 2)
        underline_end = (pos[0] + text_largueur / 2, pos[1] + text_hauteur / 2)
        pygame.draw.line(surface, underline_color, underline_start, underline_end, 2)
    position = text_surface.get_rect(center=pos or (surface.get_width() / 2, surface.get_height() / 2))
    surface.blit(text_surface, position)