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


def cell_to_pixel(cell):
    row, col = cell
    x = BOARD_OFFSET_X + col * TILE_SIZE
    y = BOARD_OFFSET_Y + row * TILE_SIZE
    return x, y


def lerp_point(start, end, t):
    start_x, start_y = start
    end_x, end_y = end
    return start_x + (end_x - start_x) * t, start_y + (end_y - start_y) * t


def draw_grid(surface, grid, selected_cell=None, swap_animation=None, fall_animation=None):
    animating_cells = set()
    if swap_animation is not None:
        animating_cells |= {swap_animation["cell_a"], swap_animation["cell_b"]}
    if fall_animation is not None:
        animating_cells |= set(fall_animation["offsets"].keys())

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if (row, col) in animating_cells:
                continue
            if grid[row][col] is None:
                continue
            color = CANDY_COLORS[grid[row][col]]
            x, y = cell_to_pixel((row, col))
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)
            if selected_cell == (row, col):
                pygame.draw.rect(surface, SELECTION_COLOR, rect, SELECTION_BORDER_WIDTH)

    if swap_animation is not None:
        draw_swapping_tiles(surface, grid, swap_animation)
    if fall_animation is not None:
        draw_falling_tiles(surface, grid, fall_animation)


def draw_swapping_tiles(surface, grid, swap_animation):
    cell_a = swap_animation["cell_a"]
    cell_b = swap_animation["cell_b"]
    progress = swap_animation["progress"]

    for from_cell, to_cell in ((cell_b, cell_a), (cell_a, cell_b)):
        color = CANDY_COLORS[grid[to_cell[0]][to_cell[1]]]
        x, y = lerp_point(cell_to_pixel(from_cell), cell_to_pixel(to_cell), progress)
        pygame.draw.rect(surface, color, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))


def draw_falling_tiles(surface, grid, fall_animation):
    progress = fall_animation["progress"]
    for (final_row, col), start_row in fall_animation["offsets"].items():
        color = CANDY_COLORS[grid[final_row][col]]
        start_pos = cell_to_pixel((start_row, col))
        end_pos = cell_to_pixel((final_row, col))
        x, y = lerp_point(start_pos, end_pos, progress)
        pygame.draw.rect(surface, color, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))


def pixel_to_cell(pos):
    x, y = pos
    col = (x - BOARD_OFFSET_X) // TILE_SIZE
    row = (y - BOARD_OFFSET_Y) // TILE_SIZE
    return row, col


def is_within_grid(cell):
    row, col = cell
    return 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS


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


def compute_fall_offsets(grid):
    offsets = {}
    for col in range(GRID_COLS):
        non_empty_rows = [row for row in range(GRID_ROWS) if grid[row][col] is not None]
        empty_count = GRID_ROWS - len(non_empty_rows)
        for i, start_row in enumerate(non_empty_rows):
            final_row = empty_count + i
            if final_row != start_row:
                offsets[(final_row, col)] = start_row
    return offsets


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
    cleared_count = 0
    while matched_cells:
        cleared_count += len(matched_cells)
        clear_matches(grid, matched_cells)
        apply_gravity(grid)
        refill_empty(grid)
        matched_cells = find_matches(grid)
    return cleared_count
