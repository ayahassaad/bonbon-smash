import math

import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    TITLE_COLOR,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    BUTTON_TEXT_COLOR,
    LEVEL_PATH_VISIBLE_COUNT,
    LEVEL_PATH_TOP_MARGIN,
    LEVEL_PATH_VERTICAL_GAP,
    LEVEL_PATH_AMPLITUDE,
    LEVEL_PATH_LINE_COLOR,
    LEVEL_NODE_RADIUS,
    LEVEL_NODE_LOCKED_COLOR,
    LEVEL_NODE_UNLOCKED_COLOR,
    LEVEL_NODE_COMPLETE_COLOR,
    BACK_BUTTON_WIDTH,
    BACK_BUTTON_HEIGHT,
    BACK_BUTTON_MARGIN,
)
from grid import draw_grid, cell_to_pixel, get_tile_size


def draw_button(surface, rect, label, font):
    pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=10)
    text_surface = font.render(label, True, BUTTON_TEXT_COLOR)
    surface.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_back_button(surface, button_font, label="Back"):
    rect = pygame.Rect(BACK_BUTTON_MARGIN, BACK_BUTTON_MARGIN, BACK_BUTTON_WIDTH, BACK_BUTTON_HEIGHT)
    draw_button(surface, rect, label, button_font)
    return rect


def draw_menu(surface, title_font, button_font):
    title_surface = title_font.render("Bonbon Smash", True, TITLE_COLOR)
    title_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
    surface.blit(title_surface, title_surface.get_rect(center=title_pos))

    play_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    play_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
    draw_button(surface, play_rect, "Play", button_font)

    return {"play": play_rect}


def draw_level_path(surface, title_font, button_font, unlocked_level):
    title_surface = title_font.render("Select Level", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50)))

    start = max(0, unlocked_level - LEVEL_PATH_VISIBLE_COUNT // 2)
    indices = list(range(start, start + LEVEL_PATH_VISIBLE_COUNT))

    positions = {}
    for i, level_index in enumerate(indices):
        x = WINDOW_WIDTH // 2 + LEVEL_PATH_AMPLITUDE * math.sin(i * math.pi / 3)
        y = LEVEL_PATH_TOP_MARGIN + i * LEVEL_PATH_VERTICAL_GAP
        positions[level_index] = (x, y)

    for i in range(len(indices) - 1):
        pygame.draw.line(
            surface, LEVEL_PATH_LINE_COLOR, positions[indices[i]], positions[indices[i + 1]], 4
        )

    level_rects = {}
    for level_index in indices:
        x, y = positions[level_index]
        if level_index < unlocked_level:
            color = LEVEL_NODE_COMPLETE_COLOR
        elif level_index == unlocked_level:
            color = LEVEL_NODE_UNLOCKED_COLOR
        else:
            color = LEVEL_NODE_LOCKED_COLOR

        pygame.draw.circle(surface, color, (x, y), LEVEL_NODE_RADIUS)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), LEVEL_NODE_RADIUS, 2)

        label_surface = button_font.render(str(level_index + 1), True, BUTTON_TEXT_COLOR)
        surface.blit(label_surface, label_surface.get_rect(center=(x, y)))

        if level_index <= unlocked_level:
            rect = pygame.Rect(0, 0, LEVEL_NODE_RADIUS * 2, LEVEL_NODE_RADIUS * 2)
            rect.center = (x, y)
            level_rects[level_index] = rect

    back_rect = draw_back_button(surface, button_font, "Menu")

    return level_rects, back_rect


def draw_level_complete(surface, title_font, button_font, score):
    title_surface = title_font.render("Level Complete!", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 90)))

    score_surface = button_font.render(f"Score: {score}", True, BUTTON_TEXT_COLOR)
    surface.blit(score_surface, score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))

    next_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    next_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
    draw_button(surface, next_rect, "Next Level", button_font)

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


def draw_no_moves(surface, title_font, button_font, score):
    title_surface = title_font.render("No More Moves!", True, TITLE_COLOR)
    surface.blit(title_surface, title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 90)))

    score_surface = button_font.render(f"Score: {score}", True, BUTTON_TEXT_COLOR)
    surface.blit(score_surface, score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)))

    reshuffle_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    reshuffle_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
    draw_button(surface, reshuffle_rect, "Reshuffle", button_font)

    return {"reshuffle": reshuffle_rect}


def draw_tutorial(surface, title_font, button_font, board, swap_pair, step_text, is_last_step, now):
    draw_grid(surface, board, now)

    if swap_pair is not None:
        tile_size = get_tile_size()
        for cell in swap_pair:
            x, y = cell_to_pixel(cell)
            rect = pygame.Rect(x, y, tile_size, tile_size)
            pygame.draw.rect(surface, (255, 255, 255), rect, 4, border_radius=8)

    panel_rect = pygame.Rect(20, WINDOW_HEIGHT - 170, WINDOW_WIDTH - 40, 150)
    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel_surface.fill((10, 8, 20, 220))
    surface.blit(panel_surface, panel_rect.topleft)

    lines = step_text.split("\n")
    for i, line in enumerate(lines):
        line_surface = button_font.render(line, True, BUTTON_TEXT_COLOR)
        surface.blit(line_surface, line_surface.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.top + 30 + i * 32)))

    next_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
    next_rect.center = (WINDOW_WIDTH // 2, panel_rect.bottom - 35)
    draw_button(surface, next_rect, "Got it!" if is_last_step else "Next", button_font)

    skip_rect = draw_back_button(surface, button_font, "Skip")

    return {"next": next_rect, "skip": skip_rect}
