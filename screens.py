import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    TITLE_COLOR,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    BUTTON_TEXT_COLOR,
)


def draw_button(surface, rect, label, font):
    pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=10)
    text_surface = font.render(label, True, BUTTON_TEXT_COLOR)
    surface.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_menu(surface, title_font, button_font):
    title_surface = title_font.render("Bonbon Smash", True, TITLE_COLOR)
    title_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
    surface.blit(title_surface, title_surface.get_rect(center=title_pos))

    play_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    play_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
    draw_button(surface, play_rect, "Play", button_font)

    return {"play": play_rect}
