import random

import pygame

from constants import (
    GRID_ROWS,
    GRID_COLS,
    CANDY_COLORS,
    TILE_SIZE,
    BOARD_OFFSET_X,
    BOARD_OFFSET_Y,
    SELECTION_COLOR,
    SELECTION_BORDER_WIDTH,
)


def create_grid():
    return [
        [random.randint(0, len(CANDY_COLORS) - 1) for _ in range(GRID_COLS)]
        for _ in range(GRID_ROWS)
    ]


def draw_grid(surface, grid, selected_cell=None):
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
            if selected_cell == (row, col):
                pygame.draw.rect(surface, SELECTION_COLOR, rect, SELECTION_BORDER_WIDTH)


def pixel_to_cell(pos):
    x, y = pos
    col = (x - BOARD_OFFSET_X) // TILE_SIZE
    row = (y - BOARD_OFFSET_Y) // TILE_SIZE
    return row, col


def is_adjacent(cell_a, cell_b):
    row_a, col_a = cell_a
    row_b, col_b = cell_b
    return abs(row_a - row_b) + abs(col_a - col_b) == 1


def swap_cells(grid, cell_a, cell_b):
    row_a, col_a = cell_a
    row_b, col_b = cell_b
    grid[row_a][col_a], grid[row_b][col_b] = grid[row_b][col_b], grid[row_a][col_a]
