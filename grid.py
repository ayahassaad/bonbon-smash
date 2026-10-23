import random

import pygame

from constants import (
    GRID_ROWS,
    GRID_COLS,
    CANDY_COLORS,
    TILE_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
)


def create_grid():
    return [
        [random.randint(0, len(CANDY_COLORS) - 1) for _ in range(GRID_COLS)]
        for _ in range(GRID_ROWS)
    ]


def draw_grid(surface, grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            color = CANDY_COLORS[grid[row][col]]
            rect = pygame.Rect(
                BOARD_OFFSET_X + col * TILE_SIZE,
                BOARD_OFFSET_Y + row * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            )
            pygame.draw.rect(surface, color, rect)
