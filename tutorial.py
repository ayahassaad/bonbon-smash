import random

from grid import configure_board, create_grid, make_candy, find_matches, swap_cells

TUTORIAL_GRID_SIZE = 5
TUTORIAL_COLORS = 4
TUTORIAL_SEED = 42

TUTORIAL_STEPS = [
    "Tap two neighboring candies to swap them.\nLine up 3 or more of the same shape to clear them!",
    "Match 4 in a row to create a striped candy.\nIt clears a whole row or column when matched!",
    "Match 5 in a row to create a bomb.\nIt clears every candy of that color on the board!",
    "Each level gives you a limited number of moves\nto reach the target score. Good luck out there!",
]


def _find_demo_swap(board):
    size = TUTORIAL_GRID_SIZE
    for row in range(size):
        for col in range(size):
            for dr, dc in ((0, 1), (1, 0)):
                row2, col2 = row + dr, col + dc
                if row2 >= size or col2 >= size:
                    continue
                swap_cells(board, (row, col), (row2, col2))
                matched = find_matches(board)
                swap_cells(board, (row, col), (row2, col2))
                if matched:
                    return (row, col), (row2, col2)
    return None


def build_tutorial_board():
    configure_board(TUTORIAL_GRID_SIZE, TUTORIAL_GRID_SIZE, TUTORIAL_COLORS)

    rng_state = random.getstate()
    random.seed(TUTORIAL_SEED)
    board = create_grid()
    random.setstate(rng_state)

    swap_pair = _find_demo_swap(board)
    board[0][0] = make_candy(0, "row")
    board[TUTORIAL_GRID_SIZE - 1][TUTORIAL_GRID_SIZE - 1] = make_candy(1, "bomb")

    return board, swap_pair
