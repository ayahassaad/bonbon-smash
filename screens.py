import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    TITLE_COLOR,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    BUTTON_TEXT_COLOR,
    LEVEL_BOX_SIZE,
    LEVEL_BOX_GAP,
    LEVEL_BOX_COLUMNS,
    LEVEL_BOX_LOCKED_COLOR,
    LEVEL_BOX_UNLOCKED_COLOR,
    LEVEL_BOX_COMPLETE_COLOR,
)
from levels import LEVELS


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


def draw_level_select(surface, title_font, button_font, unlocked_level):
    title_surface = title_font.render("Select Level", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, 60)))

    total_width = LEVEL_BOX_COLUMNS * LEVEL_BOX_SIZE + (LEVEL_BOX_COLUMNS - 1) * LEVEL_BOX_GAP
    start_x = (WINDOW_WIDTH - total_width) // 2
    start_y = 130

    level_rects = {}
    for index in range(len(LEVELS)):
        row, col = divmod(index, LEVEL_BOX_COLUMNS)
        x = start_x + col * (LEVEL_BOX_SIZE + LEVEL_BOX_GAP)
        y = start_y + row * (LEVEL_BOX_SIZE + LEVEL_BOX_GAP)
        rect = pygame.Rect(x, y, LEVEL_BOX_SIZE, LEVEL_BOX_SIZE)

        if index < unlocked_level:
            color = LEVEL_BOX_COMPLETE_COLOR
        elif index == unlocked_level:
            color = LEVEL_BOX_UNLOCKED_COLOR
        else:
            color = LEVEL_BOX_LOCKED_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=8)

        label_surface = button_font.render(str(index + 1), True, BUTTON_TEXT_COLOR)
        surface.blit(label_surface, label_surface.get_rect(center=rect.center))

        if index <= unlocked_level:
            level_rects[index] = rect

    return level_rects


def draw_level_complete(surface, title_font, button_font, score, is_last_level):
    title_surface = title_font.render("Level Complete!", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 90)))

    score_surface = button_font.render(f"Score: {score}", True, BUTTON_TEXT_COLOR)
    surface.blit(score_surface, score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))

    next_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    next_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
    draw_button(surface, next_rect, "Menu" if is_last_level else "Next Level", button_font)

    return {"next": next_rect}


def draw_game_over(surface, title_font, button_font, score, target_score):
    title_surface = title_font.render("Out of Moves", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 90)))

    score_surface = button_font.render(f"Score: {score} / {target_score}", True, BUTTON_TEXT_COLOR)
    surface.blit(score_surface, score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))

    retry_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    retry_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
    draw_button(surface, retry_rect, "Retry", button_font)

    return {"retry": retry_rect}
