import asyncio

import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BACKGROUND_COLOR,
    SCORE_PER_TILE,
    SCORE_FONT_SIZE,
    SCORE_COLOR,
    SCORE_POSITION,
    MOVES_COLOR,
    MOVES_POSITION,
    TITLE_FONT_SIZE,
    BUTTON_FONT_SIZE,
    SWAP_ANIMATION_DURATION_MS,
    FALL_ANIMATION_DURATION_MS,
    SWAP_SOUND_PATH,
    MATCH_SOUND_PATH,
    CASCADE_SOUND_PATH,
    WIN_SOUND_PATH,
    LOSE_SOUND_PATH,
    STATE_MENU,
    STATE_LEVEL_SELECT,
    STATE_PLAYING,
    STATE_LEVEL_COMPLETE,
    STATE_GAME_OVER,
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
from particles import spawn_particles_for_matches, update_and_draw_particles
from levels import LEVELS, load_unlocked_level, save_unlocked_level
from screens import draw_menu, draw_level_select, draw_level_complete, draw_game_over


def try_start_fall(grid):
    matched_cells = find_matches(grid)
    if not matched_cells:
        return None, 0, []
    new_particles = spawn_particles_for_matches(grid, matched_cells)
    animation = {
        "offsets": start_fall(grid, matched_cells),
        "start_time": pygame.time.get_ticks(),
        "progress": 0.0,
    }
    return animation, len(matched_cells) * SCORE_PER_TILE, new_particles


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bonbon Smash")
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
    title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
    button_font = pygame.font.SysFont(None, BUTTON_FONT_SIZE)
    swap_sound = pygame.mixer.Sound(SWAP_SOUND_PATH)
    match_sound = pygame.mixer.Sound(MATCH_SOUND_PATH)
    cascade_sound = pygame.mixer.Sound(CASCADE_SOUND_PATH)
    win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
    lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)

    state = STATE_MENU
    unlocked_level = load_unlocked_level()
    current_level = 0

    grid = None
    selected_cell = None
    score = 0
    moves_remaining = 0
    swap_animation = None
    fall_animation = None
    particles = []
    buttons = {}
    level_rects = {}

    def start_level(level_index):
        nonlocal grid, selected_cell, score, moves_remaining, swap_animation, fall_animation, particles, current_level
        current_level = level_index
        grid = create_grid()
        selected_cell = None
        score = 0
        moves_remaining = LEVELS[level_index]["move_limit"]
        swap_animation = None
        fall_animation = None
        particles = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU:
                    if buttons.get("play") and buttons["play"].collidepoint(event.pos):
                        state = STATE_LEVEL_SELECT
                elif state == STATE_LEVEL_SELECT:
                    if buttons.get("back") and buttons["back"].collidepoint(event.pos):
                        state = STATE_MENU
                    else:
                        for index, rect in level_rects.items():
                            if rect.collidepoint(event.pos):
                                start_level(index)
                                state = STATE_PLAYING
                                break
                elif state == STATE_PLAYING:
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
                        swap_sound.play()
                        swap_animation = {
                            "cell_a": selected_cell,
                            "cell_b": clicked_cell,
                            "start_time": pygame.time.get_ticks(),
                        }
                        selected_cell = None
                    else:
                        selected_cell = clicked_cell
                elif state == STATE_LEVEL_COMPLETE:
                    if buttons.get("next") and buttons["next"].collidepoint(event.pos):
                        if current_level + 1 < len(LEVELS):
                            start_level(current_level + 1)
                            state = STATE_PLAYING
                        else:
                            state = STATE_MENU
                elif state == STATE_GAME_OVER:
                    if buttons.get("retry") and buttons["retry"].collidepoint(event.pos):
                        start_level(current_level)
                        state = STATE_PLAYING

        if state == STATE_PLAYING and swap_animation is not None:
            elapsed = pygame.time.get_ticks() - swap_animation["start_time"]
            if elapsed >= SWAP_ANIMATION_DURATION_MS:
                fall_animation, score_delta, new_particles = try_start_fall(grid)
                if fall_animation is not None:
                    match_sound.play()
                    score += score_delta
                    moves_remaining -= 1
                    particles.extend(new_particles)
                else:
                    swap_cells(grid, swap_animation["cell_a"], swap_animation["cell_b"])
                swap_animation = None
            else:
                swap_animation["progress"] = elapsed / SWAP_ANIMATION_DURATION_MS

        if state == STATE_PLAYING and fall_animation is not None:
            elapsed = pygame.time.get_ticks() - fall_animation["start_time"]
            if elapsed >= FALL_ANIMATION_DURATION_MS:
                fall_animation, score_delta, new_particles = try_start_fall(grid)
                if fall_animation is not None:
                    cascade_sound.play()
                score += score_delta
                particles.extend(new_particles)
            else:
                fall_animation["progress"] = elapsed / FALL_ANIMATION_DURATION_MS

        if state == STATE_PLAYING and swap_animation is None and fall_animation is None:
            target_score = LEVELS[current_level]["target_score"]
            if score >= target_score:
                newly_unlocked = min(current_level + 1, len(LEVELS) - 1)
                if newly_unlocked > unlocked_level:
                    unlocked_level = newly_unlocked
                    save_unlocked_level(unlocked_level)
                win_sound.play()
                state = STATE_LEVEL_COMPLETE
            elif moves_remaining <= 0:
                lose_sound.play()
                state = STATE_GAME_OVER

        screen.fill(BACKGROUND_COLOR)
        buttons = {}
        if state == STATE_MENU:
            buttons = draw_menu(screen, title_font, button_font)
        elif state == STATE_LEVEL_SELECT:
            level_rects, back_rect = draw_level_select(screen, title_font, button_font, unlocked_level)
            buttons = {"back": back_rect}
        elif state == STATE_PLAYING:
            draw_grid(screen, grid, selected_cell, swap_animation, fall_animation)
            particles = update_and_draw_particles(screen, particles, pygame.time.get_ticks())
            score_surface = score_font.render(f"Score: {score}", True, SCORE_COLOR)
            screen.blit(score_surface, SCORE_POSITION)
            moves_surface = score_font.render(f"Moves: {moves_remaining}", True, MOVES_COLOR)
            screen.blit(moves_surface, MOVES_POSITION)
        elif state == STATE_LEVEL_COMPLETE:
            buttons = draw_level_complete(
                screen, title_font, button_font, score, current_level + 1 >= len(LEVELS)
            )
        elif state == STATE_GAME_OVER:
            buttons = draw_game_over(
                screen, title_font, button_font, score, LEVELS[current_level]["target_score"]
            )
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
