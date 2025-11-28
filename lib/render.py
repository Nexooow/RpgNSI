import pygame

def text_render (text, font, color=(0, 0, 0)):
    if font == "extrabold":
        font = pygame.font.Font("./assets/CinzelDecorative-Black.ttf", 56)
    elif font == "bold":
        font = pygame.font.Font("./assets/CinzelDecorative-Bold.ttf", 48)
    else:
        font = pygame.font.Font("./assets/CinzelDecorative-Regular.ttf", 36)
    return font.render(text, True, color)
    
    
def text_render_centered(screen, text, font, color=(0, 0, 0), pos=(0, 0), underline = False):
    text_surface = text_render(text, font, color)
    if underline:
        text_largueur, text_hauteur = text_surface.get_size()
        underline_start = (pos[0] - text_largueur / 2, pos[1] + text_hauteur / 2)
        underline_end = (pos[0] + text_largueur / 2, pos[1] + text_hauteur / 2)
        pygame.draw.line(screen, color, underline_start, underline_end, 2)
    position = text_surface.get_rect(center=pos or (screen.get_width() / 2, screen.get_height() / 2))
    screen.blit(text_surface, position)
