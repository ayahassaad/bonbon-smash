import math
import random

import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    STAR_COUNT,
    STAR_COLOR,
    STAR_TWINKLE_PERIOD_MS,
)


def create_stars():
    return [
        {
            "x": random.uniform(0, WINDOW_WIDTH),
            "y": random.uniform(0, WINDOW_HEIGHT),
            "radius": random.uniform(1, 2.5),
            "phase": random.uniform(0, 2 * math.pi),
        }
        for _ in range(STAR_COUNT)
    ]


def draw_stars(surface, stars, now):
    for star in stars:
        twinkle = 0.5 + 0.5 * math.sin((now / STAR_TWINKLE_PERIOD_MS) * 2 * math.pi + star["phase"])
        alpha = int(90 + twinkle * 165)
        star_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (*STAR_COLOR, alpha), (3, 3), star["radius"])
        surface.blit(star_surface, (star["x"] - 3, star["y"] - 3))
