import pygame

from constants import CANDY_COLORS, BEAM_DURATION_MS, BEAM_THICKNESS
from grid import cell_to_pixel, get_tile_size, get_board_dimensions


def spawn_beams_for_specials(activated_specials):
    beams = []
    now = pygame.time.get_ticks()
    for item in activated_specials:
        if item["type"] not in ("row", "col", "cross"):
            continue
        beams.append({
            "cell": item["cell"],
            "type": item["type"],
            "color": CANDY_COLORS[item["color"]],
            "start_time": now,
        })
    return beams


def update_and_draw_beams(surface, beams, now):
    alive = []
    tile_size = get_tile_size()
    rows, cols = get_board_dimensions()
    board_x, board_y = cell_to_pixel((0, 0))

    for beam in beams:
        elapsed = now - beam["start_time"]
        if elapsed >= BEAM_DURATION_MS:
            continue

        progress = elapsed / BEAM_DURATION_MS
        alpha = int(255 * (1 - progress))
        row, col = beam["cell"]
        x, y = cell_to_pixel((row, col))
        cx, cy = x + tile_size / 2, y + tile_size / 2

        beam_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        if beam["type"] in ("row", "cross"):
            extent = progress * cols * tile_size
            left = max(board_x, cx - extent)
            right = min(board_x + cols * tile_size, cx + extent)
            rect = pygame.Rect(left, cy - BEAM_THICKNESS / 2, max(right - left, 1), BEAM_THICKNESS)
            pygame.draw.rect(beam_surface, (*beam["color"], alpha), rect, border_radius=BEAM_THICKNESS // 2)

        if beam["type"] in ("col", "cross"):
            extent = progress * rows * tile_size
            top = max(board_y, cy - extent)
            bottom = min(board_y + rows * tile_size, cy + extent)
            rect = pygame.Rect(cx - BEAM_THICKNESS / 2, top, BEAM_THICKNESS, max(bottom - top, 1))
            pygame.draw.rect(beam_surface, (*beam["color"], alpha), rect, border_radius=BEAM_THICKNESS // 2)

        surface.blit(beam_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        alive.append(beam)

    return alive
