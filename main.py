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
    FALL_SPEED_PIXELS_PER_SEC,
    MIN_FALL_DURATION_MS,
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
    STATE_NO_MOVES,
    STATE_TUTORIAL,
    FADE_DURATION_MS,
    FADE_COLOR,
)
from grid import (
    configure_board,
    create_grid,
    draw_grid,
    pixel_to_cell,
    is_within_grid,
    is_adjacent,
    swap_cells,
    analyze_matches,
    start_fall,
    has_possible_moves,
    get_tile_size,
)
from particles import spawn_particles_for_matches, update_and_draw_particles
from levels import (
    get_level,
    load_unlocked_level,
    save_unlocked_level,
    load_tutorial_seen,
    mark_tutorial_seen,
)
from screens import (
    draw_menu,
    draw_level_path,
    draw_level_complete,
    draw_game_over,
    draw_no_moves,
    draw_back_button,
    draw_tutorial,
)
from starfield import create_stars, draw_stars
from tutorial import build_tutorial_board, TUTORIAL_STEPS


def try_start_fall(grid):
    matched_cells, special_spawns = analyze_matches(grid)
    if not matched_cells:
        return None, 0, []
    new_particles = spawn_particles_for_matches(grid, matched_cells)
    offsets = start_fall(grid, matched_cells, special_spawns)
    if offsets:
        max_distance = max(final_row - start_row for (final_row, _col), start_row in offsets.items())
    else:
        max_distance = 0
    duration = max(MIN_FALL_DURATION_MS, max_distance * get_tile_size() / FALL_SPEED_PIXELS_PER_SEC * 1000)
    animation = {
        "offsets": offsets,
        "duration": duration,
        "start_time": pygame.time.get_ticks(),
        "progress": 0.0,
    }
    return animation, len(matched_cells) * SCORE_PER_TILE, new_particles


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bonbon Smash")
    clock = pygame.time.Clock()
    fade_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_overlay.fill(FADE_COLOR)
    fade_start_time = pygame.time.get_ticks()
    stars = create_stars()
    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
    title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
    button_font = pygame.font.SysFont(None, BUTTON_FONT_SIZE)
    swap_sound = pygame.mixer.Sound(SWAP_SOUND_PATH)
    match_sound = pygame.mixer.Sound(MATCH_SOUND_PATH)
    cascade_sound = pygame.mixer.Sound(CASCADE_SOUND_PATH)
    win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
    lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)

    tutorial_board, tutorial_swap_pair = build_tutorial_board()
    tutorial_step = 0

    unlocked_level = load_unlocked_level()
    state = STATE_MENU if load_tutorial_seen() else STATE_TUTORIAL
    previous_state = state
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
        level = get_level(level_index)
        configure_board(level["rows"], level["cols"], level["colors"])
        grid = create_grid()
        selected_cell = None
        score = 0
        moves_remaining = level["move_limit"]
        swap_animation = None
        fall_animation = None
        particles = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_TUTORIAL:
                    if buttons.get("skip") and buttons["skip"].collidepoint(event.pos):
                        mark_tutorial_seen()
                        state = STATE_MENU
                    elif buttons.get("next") and buttons["next"].collidepoint(event.pos):
                        if tutorial_step >= len(TUTORIAL_STEPS) - 1:
                            mark_tutorial_seen()
                            state = STATE_MENU
                        else:
                            tutorial_step += 1
                elif state == STATE_MENU:
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
                    if buttons.get("back") and buttons["back"].collidepoint(event.pos):
                        state = STATE_LEVEL_SELECT
                        continue
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
                        start_level(current_level + 1)
                        state = STATE_PLAYING
                elif state == STATE_GAME_OVER:
                    if buttons.get("retry") and buttons["retry"].collidepoint(event.pos):
                        start_level(current_level)
                        state = STATE_PLAYING
                elif state == STATE_NO_MOVES:
                    if buttons.get("reshuffle") and buttons["reshuffle"].collidepoint(event.pos):
                        grid = create_grid()
                        selected_cell = None
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
            duration = fall_animation["duration"]
            if elapsed >= duration:
                fall_animation, score_delta, new_particles = try_start_fall(grid)
                if fall_animation is not None:
                    cascade_sound.play()
                score += score_delta
                particles.extend(new_particles)
            else:
                fall_animation["progress"] = elapsed / duration

        if state == STATE_PLAYING and swap_animation is None and fall_animation is None:
            target_score = get_level(current_level)["target_score"]
            if score >= target_score:
                newly_unlocked = current_level + 1
                if newly_unlocked > unlocked_level:
                    unlocked_level = newly_unlocked
                    save_unlocked_level(unlocked_level)
                win_sound.play()
                state = STATE_LEVEL_COMPLETE
            elif moves_remaining <= 0:
                lose_sound.play()
                state = STATE_GAME_OVER
            elif not has_possible_moves(grid):
                state = STATE_NO_MOVES

        if state != previous_state:
            fade_start_time = pygame.time.get_ticks()
            previous_state = state

        screen.fill(BACKGROUND_COLOR)
        draw_stars(screen, stars, pygame.time.get_ticks())
        buttons = {}
        if state == STATE_TUTORIAL:
            swap_pair_to_show = tutorial_swap_pair if tutorial_step == 0 else None
            is_last_step = tutorial_step == len(TUTORIAL_STEPS) - 1
            buttons = draw_tutorial(
                screen,
                title_font,
                button_font,
                tutorial_board,
                swap_pair_to_show,
                TUTORIAL_STEPS[tutorial_step],
                is_last_step,
                pygame.time.get_ticks(),
            )
        elif state == STATE_MENU:
            buttons = draw_menu(screen, title_font, button_font)
        elif state == STATE_LEVEL_SELECT:
            level_rects, back_rect = draw_level_path(screen, title_font, button_font, unlocked_level)
            buttons = {"back": back_rect}
        elif state == STATE_PLAYING:
            draw_grid(screen, grid, pygame.time.get_ticks(), selected_cell, swap_animation, fall_animation)
            particles = update_and_draw_particles(screen, particles, pygame.time.get_ticks())
            target_score = get_level(current_level)["target_score"]
            score_surface = score_font.render(f"Score: {score} / {target_score}", True, SCORE_COLOR)
            screen.blit(score_surface, SCORE_POSITION)
            moves_surface = score_font.render(f"Moves: {moves_remaining}", True, MOVES_COLOR)
            screen.blit(moves_surface, MOVES_POSITION)
            buttons = {"back": draw_back_button(screen, button_font)}
        elif state == STATE_LEVEL_COMPLETE:
            buttons = draw_level_complete(screen, title_font, button_font, score)
        elif state == STATE_GAME_OVER:
            buttons = draw_game_over(
                screen, title_font, button_font, score, get_level(current_level)["target_score"]
            )
        elif state == STATE_NO_MOVES:
            buttons = draw_no_moves(screen, title_font, button_font, score)

        fade_elapsed = pygame.time.get_ticks() - fade_start_time
        if fade_elapsed < FADE_DURATION_MS:
            fade_overlay.set_alpha(int(255 * (1 - fade_elapsed / FADE_DURATION_MS)))
            screen.blit(fade_overlay, (0, 0))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
