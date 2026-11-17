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
from sprites import draw_candy

BOARD_AREA = GRID_COLS * TILE_SIZE

BOARD = {
    "rows": GRID_ROWS,
    "cols": GRID_COLS,
    "tile_size": TILE_SIZE,
    "offset_x": BOARD_OFFSET_X,
    "offset_y": BOARD_OFFSET_Y,
    "colors": len(CANDY_COLORS),
}


def configure_board(rows, cols, colors):
    tile_size = BOARD_AREA // max(rows, cols)
    BOARD["rows"] = rows
    BOARD["cols"] = cols
    BOARD["tile_size"] = tile_size
    BOARD["offset_x"] = (BOARD_AREA - cols * tile_size) // 2
    BOARD["offset_y"] = BOARD_OFFSET_Y + (BOARD_AREA - rows * tile_size) // 2
    BOARD["colors"] = colors


def get_tile_size():
    return BOARD["tile_size"]


def make_candy(color_index, special=None):
    return {"color": color_index, "special": special}


def create_grid():
    rows, cols, colors = BOARD["rows"], BOARD["cols"], BOARD["colors"]
    grid = [[None for _ in range(cols)] for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            forbidden = set()
            if col >= 2 and grid[row][col - 1]["color"] == grid[row][col - 2]["color"]:
                forbidden.add(grid[row][col - 1]["color"])
            if row >= 2 and grid[row - 1][col]["color"] == grid[row - 2][col]["color"]:
                forbidden.add(grid[row - 1][col]["color"])
            choices = [c for c in range(colors) if c not in forbidden]
            grid[row][col] = make_candy(random.choice(choices))
    return grid


def cell_to_pixel(cell):
    row, col = cell
    tile_size = BOARD["tile_size"]
    x = BOARD["offset_x"] + col * tile_size
    y = BOARD["offset_y"] + row * tile_size
    return x, y


def lerp_point(start, end, t):
    start_x, start_y = start
    end_x, end_y = end
    return start_x + (end_x - start_x) * t, start_y + (end_y - start_y) * t


def draw_grid(surface, grid, now, selected_cell=None, swap_animation=None, fall_animation=None):
    tile_size = BOARD["tile_size"]
    animating_cells = set()
    if swap_animation is not None:
        animating_cells |= {swap_animation["cell_a"], swap_animation["cell_b"]}
    if fall_animation is not None:
        animating_cells |= set(fall_animation["offsets"].keys())

    for row in range(BOARD["rows"]):
        for col in range(BOARD["cols"]):
            if (row, col) in animating_cells:
                continue
            if grid[row][col] is None:
                continue
            candy = grid[row][col]
            x, y = cell_to_pixel((row, col))
            rect = pygame.Rect(x, y, tile_size, tile_size)
            draw_candy(surface, rect, candy["color"], CANDY_COLORS[candy["color"]], candy["special"], now)
            if selected_cell == (row, col):
                pygame.draw.rect(surface, SELECTION_COLOR, rect, SELECTION_BORDER_WIDTH)

    if swap_animation is not None:
        draw_swapping_tiles(surface, grid, swap_animation, now)
    if fall_animation is not None:
        draw_falling_tiles(surface, grid, fall_animation, now)


def draw_swapping_tiles(surface, grid, swap_animation, now):
    tile_size = BOARD["tile_size"]
    cell_a = swap_animation["cell_a"]
    cell_b = swap_animation["cell_b"]
    progress = swap_animation["progress"]

    for from_cell, to_cell in ((cell_b, cell_a), (cell_a, cell_b)):
        candy = grid[to_cell[0]][to_cell[1]]
        x, y = lerp_point(cell_to_pixel(from_cell), cell_to_pixel(to_cell), progress)
        rect = pygame.Rect(x, y, tile_size, tile_size)
        draw_candy(surface, rect, candy["color"], CANDY_COLORS[candy["color"]], candy["special"], now)


def draw_falling_tiles(surface, grid, fall_animation, now):
    tile_size = BOARD["tile_size"]
    progress = fall_animation["progress"]
    for (final_row, col), start_row in fall_animation["offsets"].items():
        candy = grid[final_row][col]
        start_pos = cell_to_pixel((start_row, col))
        end_pos = cell_to_pixel((final_row, col))
        x, y = lerp_point(start_pos, end_pos, progress)
        rect = pygame.Rect(x, y, tile_size, tile_size)
        draw_candy(surface, rect, candy["color"], CANDY_COLORS[candy["color"]], candy["special"], now)


def pixel_to_cell(pos):
    x, y = pos
    col = (x - BOARD["offset_x"]) // BOARD["tile_size"]
    row = (y - BOARD["offset_y"]) // BOARD["tile_size"]
    return row, col


def is_within_grid(cell):
    row, col = cell
    return 0 <= row < BOARD["rows"] and 0 <= col < BOARD["cols"]


def is_adjacent(cell_a, cell_b):
    row_a, col_a = cell_a
    row_b, col_b = cell_b
    return abs(row_a - row_b) + abs(col_a - col_b) == 1


def swap_cells(grid, cell_a, cell_b):
    row_a, col_a = cell_a
    row_b, col_b = cell_b
    grid[row_a][col_a], grid[row_b][col_b] = grid[row_b][col_b], grid[row_a][col_a]


def has_possible_moves(grid):
    rows, cols = BOARD["rows"], BOARD["cols"]
    for row in range(rows):
        for col in range(cols):
            for dr, dc in ((0, 1), (1, 0)):
                row2, col2 = row + dr, col + dc
                if row2 >= rows or col2 >= cols:
                    continue
                swap_cells(grid, (row, col), (row2, col2))
                matched = find_matches(grid)
                swap_cells(grid, (row, col), (row2, col2))
                if matched:
                    return True
    return False


def find_match_runs(grid):
    rows, cols = BOARD["rows"], BOARD["cols"]
    runs = []

    for row in range(rows):
        col = 0
        while col < cols:
            match_color = grid[row][col]["color"]
            match_start = col
            while col < cols and grid[row][col]["color"] == match_color:
                col += 1
            if col - match_start >= 3:
                cells = [(row, c) for c in range(match_start, col)]
                runs.append({"cells": cells, "orientation": "row", "color": match_color})

    for col in range(cols):
        row = 0
        while row < rows:
            match_color = grid[row][col]["color"]
            match_start = row
            while row < rows and grid[row][col]["color"] == match_color:
                row += 1
            if row - match_start >= 3:
                cells = [(r, col) for r in range(match_start, row)]
                runs.append({"cells": cells, "orientation": "col", "color": match_color})

    return runs


def find_matches(grid):
    matched = set()
    for run in find_match_runs(grid):
        matched.update(run["cells"])
    return matched


def expand_special_effects(grid, matched_cells):
    rows, cols = BOARD["rows"], BOARD["cols"]
    matched = set(matched_cells)
    frontier = set(matched_cells)

    while frontier:
        triggered = set()
        for row, col in frontier:
            candy = grid[row][col]
            if candy is None:
                continue
            special = candy["special"]
            if special == "row":
                triggered.update((row, c) for c in range(cols))
            elif special == "col":
                triggered.update((r, col) for r in range(rows))
            elif special == "bomb":
                color = candy["color"]
                triggered.update(
                    (r, c)
                    for r in range(rows)
                    for c in range(cols)
                    if grid[r][c] is not None and grid[r][c]["color"] == color
                )
        triggered -= matched
        matched |= triggered
        frontier = triggered

    return matched


def analyze_matches(grid):
    runs = find_match_runs(grid)
    if not runs:
        return set(), {}

    base_matched = set()
    special_spawns = {}
    for run in runs:
        cells = run["cells"]
        base_matched.update(cells)
        if len(cells) >= 4:
            spawn_cell = cells[len(cells) // 2]
            special_type = "bomb" if len(cells) >= 5 else run["orientation"]
            special_spawns[spawn_cell] = (run["color"], special_type)

    matched_cells = expand_special_effects(grid, base_matched)
    return matched_cells, special_spawns


def apply_match_results(grid, matched_cells, special_spawns):
    for (row, col), (color, special_type) in special_spawns.items():
        grid[row][col] = make_candy(color, special_type)
    for row, col in matched_cells:
        if (row, col) not in special_spawns:
            grid[row][col] = None


def compute_fall_offsets(grid):
    rows, cols = BOARD["rows"], BOARD["cols"]
    offsets = {}
    for col in range(cols):
        non_empty_rows = [row for row in range(rows) if grid[row][col] is not None]
        empty_count = rows - len(non_empty_rows)
        for i, start_row in enumerate(non_empty_rows):
            final_row = empty_count + i
            if final_row != start_row:
                offsets[(final_row, col)] = start_row
    return offsets


def apply_gravity(grid):
    rows, cols = BOARD["rows"], BOARD["cols"]
    for col in range(cols):
        column_values = [grid[row][col] for row in range(rows) if grid[row][col] is not None]
        empty_count = rows - len(column_values)
        new_column = [None] * empty_count + column_values
        for row in range(rows):
            grid[row][col] = new_column[row]


def refill_empty(grid):
    rows, cols, colors = BOARD["rows"], BOARD["cols"], BOARD["colors"]
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] is None:
                grid[row][col] = make_candy(random.randint(0, colors - 1))


def start_fall(grid, matched_cells, special_spawns=None):
    rows, cols = BOARD["rows"], BOARD["cols"]
    apply_match_results(grid, matched_cells, special_spawns or {})
    offsets = compute_fall_offsets(grid)
    apply_gravity(grid)
    refilled_cells = [
        (row, col)
        for row in range(rows)
        for col in range(cols)
        if grid[row][col] is None
    ]
    refill_empty(grid)
    for row, col in refilled_cells:
        offsets[(row, col)] = row - rows
    return offsets
