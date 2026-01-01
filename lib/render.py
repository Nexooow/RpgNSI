import pygame


def font_render(text, font_name, color=(0, 0, 0), size=None):
    font = pygame.font.Font(
        f"./assets/fonts/{font_name}.ttf", size or 36
    )
    return font.render(text, True, color)


def underline_text(surface, text_surface, color, pos=(0, 0)):
    underline_color = (color[0], color[1], color[2], 120)
    text_largueur, text_hauteur = text_surface.get_size()
    underline_start = (pos[0] - text_largueur / 2, pos[1] + text_hauteur / 2)
    underline_end = (pos[0] + text_largueur / 2, pos[1] + text_hauteur / 2)
    pygame.draw.line(surface, underline_color, underline_start, underline_end, 2)


def text_render_centered(
        surface, text, font, color=(0, 0, 0), pos=(0, 0), underline=False, size=None
):
    text_surface = font_render(text, font, color, size)
    if underline:
        underline_text(surface, text_surface, color, pos)
    position = text_surface.get_rect(
        center=pos
    )
    surface.blit(text_surface, position)


def text_render_centered_up(
        surface, text, font, color=(0, 0, 0), pos=(0, 0), underline=False, size=None
):
    text_surface = font_render(text, font, color, size)
    if underline:
        underline_text(surface, text_surface, color, pos)
    position = text_surface.get_rect(
        center=(pos[0], pos[1] - text_surface.get_height() / 2)
    )
    surface.blit(text_surface, position)


def text_render_centered_left(
        surface, text, font, color=(0, 0, 0), pos=(0, 0), underline=False, size=None
):
    text_surface = font_render(text, font, color, size)
    if underline:
        underline_text(surface, text_surface, color, pos)
    position = text_surface.get_rect(
        center=(pos[0] + text_surface.get_width() / 2, pos[1])
    )
    surface.blit(text_surface, position)
