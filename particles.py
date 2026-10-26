import math
import random

import pygame

from constants import (
    CANDY_COLORS,
    TILE_SIZE,
    PARTICLE_COUNT_PER_TILE,
    PARTICLE_SPEED_MIN,
    PARTICLE_SPEED_MAX,
)
from grid import cell_to_pixel


def spawn_particles_for_matches(grid, matched_cells):
    particles = []
    now = pygame.time.get_ticks()
    for cell in matched_cells:
        row, col = cell
        color = CANDY_COLORS[grid[row][col]]
        x, y = cell_to_pixel(cell)
        center_x = x + TILE_SIZE / 2
        center_y = y + TILE_SIZE / 2
        for _ in range(PARTICLE_COUNT_PER_TILE):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
            particles.append({
                "x": center_x,
                "y": center_y,
                "vx": speed * math.cos(angle),
                "vy": speed * math.sin(angle),
                "color": color,
                "start_time": now,
            })
    return particles
