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
            if grid[row][col] is None:
                continue
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


def find_matches(grid):
    matched = set()

    for row in range(GRID_ROWS):
        col = 0
        while col < GRID_COLS:
            match_color = grid[row][col]
            match_start = col
            while col < GRID_COLS and grid[row][col] == match_color:
                col += 1
            if col - match_start >= 3:
                for c in range(match_start, col):
                    matched.add((row, c))

    for col in range(GRID_COLS):
        row = 0
        while row < GRID_ROWS:
            match_color = grid[row][col]
            match_start = row
            while row < GRID_ROWS and grid[row][col] == match_color:
                row += 1
            if row - match_start >= 3:
                for r in range(match_start, row):
                    matched.add((r, col))

    return matched


def clear_matches(grid, matched_cells):
    for row, col in matched_cells:
        grid[row][col] = None


def apply_gravity(grid):
    for col in range(GRID_COLS):
        column_values = [grid[row][col] for row in range(GRID_ROWS) if grid[row][col] is not None]
        empty_count = GRID_ROWS - len(column_values)
        new_column = [None] * empty_count + column_values
        for row in range(GRID_ROWS):
            grid[row][col] = new_column[row]


def refill_empty(grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if grid[row][col] is None:
                grid[row][col] = random.randint(0, len(CANDY_COLORS) - 1)


def resolve_matches(grid, matched_cells):
    while matched_cells:
        clear_matches(grid, matched_cells)
        apply_gravity(grid)
        refill_empty(grid)
        matched_cells = find_matches(grid)
