import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR, SCORE_PER_TILE
from grid import (
    create_grid,
    draw_grid,
    pixel_to_cell,
    is_within_grid,
    is_adjacent,
    swap_cells,
    find_matches,
    resolve_matches,
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bonbon Smash")
    clock = pygame.time.Clock()

    grid = create_grid()
    selected_cell = None
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_cell = pixel_to_cell(event.pos)
                if not is_within_grid(clicked_cell):
                    continue
                if selected_cell is None:
                    selected_cell = clicked_cell
                elif clicked_cell == selected_cell:
                    selected_cell = None
                elif is_adjacent(selected_cell, clicked_cell):
                    swap_cells(grid, selected_cell, clicked_cell)
                    matched_cells = find_matches(grid)
                    if matched_cells:
                        cleared_count = resolve_matches(grid, matched_cells)
                        score += cleared_count * SCORE_PER_TILE
                    else:
                        swap_cells(grid, selected_cell, clicked_cell)
                    selected_cell = None
                else:
                    selected_cell = clicked_cell

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid, selected_cell)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
