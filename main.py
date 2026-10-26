import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    SCORE_PER_TILE,
    SCORE_FONT_SIZE,
    SCORE_COLOR,
    SCORE_POSITION,
    SWAP_ANIMATION_DURATION_MS,
    FALL_ANIMATION_DURATION_MS,
)
from grid import (
    create_grid,
    draw_grid,
    pixel_to_cell,
    is_within_grid,
    is_adjacent,
    swap_cells,
    find_matches,
    start_fall,
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bonbon Smash")
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

    grid = create_grid()
    selected_cell = None
    score = 0
    swap_animation = None
    fall_animation = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if swap_animation is not None or fall_animation is not None:
                    continue
                clicked_cell = pixel_to_cell(event.pos)
                if not is_within_grid(clicked_cell):
                    continue
                if selected_cell is None:
                    selected_cell = clicked_cell
                elif clicked_cell == selected_cell:
                    selected_cell = None
                elif is_adjacent(selected_cell, clicked_cell):
                    swap_cells(grid, selected_cell, clicked_cell)
                    swap_animation = {
                        "cell_a": selected_cell,
                        "cell_b": clicked_cell,
                        "start_time": pygame.time.get_ticks(),
                    }
                    selected_cell = None
                else:
                    selected_cell = clicked_cell

        if swap_animation is not None:
            elapsed = pygame.time.get_ticks() - swap_animation["start_time"]
            if elapsed >= SWAP_ANIMATION_DURATION_MS:
                matched_cells = find_matches(grid)
                if matched_cells:
                    score += len(matched_cells) * SCORE_PER_TILE
                    fall_animation = {
                        "offsets": start_fall(grid, matched_cells),
                        "start_time": pygame.time.get_ticks(),
                        "progress": 0.0,
                    }
                else:
                    swap_cells(grid, swap_animation["cell_a"], swap_animation["cell_b"])
                swap_animation = None
            else:
                swap_animation["progress"] = elapsed / SWAP_ANIMATION_DURATION_MS

        if fall_animation is not None:
            elapsed = pygame.time.get_ticks() - fall_animation["start_time"]
            if elapsed >= FALL_ANIMATION_DURATION_MS:
                fall_animation = None
            else:
                fall_animation["progress"] = elapsed / FALL_ANIMATION_DURATION_MS

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid, selected_cell, swap_animation, fall_animation)
        score_surface = score_font.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_surface, SCORE_POSITION)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
