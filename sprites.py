import math

import pygame

SHAPES = ["orb", "diamond", "star", "ring", "comet", "hexagon"]

GLOW_LAYERS = [(9, 35), (6, 70), (3, 140)]
CORE_COLOR = (255, 255, 255)
CORE_WIDTH = 2
CORE_DOT_RADIUS = 3
TILE_PADDING = 1.3
PULSE_AMOUNT = 0.06
PULSE_PERIOD_MS = 1400


def regular_polygon_points(center, radius, sides, rotation=0.0):
    cx, cy = center
    return [
        (
            cx + radius * math.cos(rotation + i * (2 * math.pi / sides)),
            cy + radius * math.sin(rotation + i * (2 * math.pi / sides)),
        )
        for i in range(sides)
    ]


def star_points(center, outer_radius, inner_radius, rotation=-math.pi / 2):
    cx, cy = center
    points = []
    for i in range(10):
        angle = rotation + i * (math.pi / 5)
        r = outer_radius if i % 2 == 0 else inner_radius
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


def neon_polygon(surface, points, color):
    for width, alpha in GLOW_LAYERS:
        pygame.draw.polygon(surface, (*color, alpha), points, width)
    pygame.draw.polygon(surface, CORE_COLOR, points, CORE_WIDTH)


def neon_circle(surface, center, radius, color):
    for width, alpha in GLOW_LAYERS:
        pygame.draw.circle(surface, (*color, alpha), center, radius, width)
    pygame.draw.circle(surface, CORE_COLOR, center, radius, CORE_WIDTH)


def neon_ellipse(surface, rect, color):
    for width, alpha in GLOW_LAYERS:
        pygame.draw.ellipse(surface, (*color, alpha), rect, width)
    pygame.draw.ellipse(surface, CORE_COLOR, rect, CORE_WIDTH)


def neon_line(surface, start, end, color):
    for width, alpha in GLOW_LAYERS:
        pygame.draw.line(surface, (*color, alpha), start, end, width)
    pygame.draw.line(surface, CORE_COLOR, start, end, CORE_WIDTH)


def draw_candy(surface, rect, color_index, color, special=None, now=0):
    shape = SHAPES[color_index % len(SHAPES)]
    size = int(rect.width * TILE_PADDING)
    tile_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)

    phase = (rect.x * 0.013 + rect.y * 0.017)
    pulse = 1.0 + PULSE_AMOUNT * math.sin(now / PULSE_PERIOD_MS * 2 * math.pi + phase)
    radius = rect.width * 0.34 * pulse

    if shape == "orb":
        neon_circle(tile_surface, center, radius, color)
        pygame.draw.circle(tile_surface, CORE_COLOR, center, CORE_DOT_RADIUS)
    elif shape == "diamond":
        neon_polygon(tile_surface, regular_polygon_points(center, radius, 4, -math.pi / 4), color)
    elif shape == "star":
        neon_polygon(tile_surface, star_points(center, radius, radius * 0.45), color)
    elif shape == "hexagon":
        neon_polygon(tile_surface, regular_polygon_points(center, radius, 6), color)
    elif shape == "ring":
        neon_circle(tile_surface, center, radius * 0.55, color)
        ring_rect = pygame.Rect(0, 0, radius * 2.2, radius * 0.8)
        ring_rect.center = center
        neon_ellipse(tile_surface, ring_rect, color)
        pygame.draw.circle(tile_surface, CORE_COLOR, center, CORE_DOT_RADIUS)
    elif shape == "comet":
        head_radius = radius * 0.5
        tail_angle = math.pi * 0.22
        direction = (math.cos(tail_angle), math.sin(tail_angle))
        tail_start = (center[0] - direction[0] * head_radius, center[1] - direction[1] * head_radius)
        tail_end = (center[0] - direction[0] * radius * 1.7, center[1] - direction[1] * radius * 1.7)
        neon_line(tile_surface, tail_start, tail_end, color)
        neon_circle(tile_surface, center, head_radius, color)
        pygame.draw.circle(tile_surface, CORE_COLOR, center, CORE_DOT_RADIUS)

    draw_special_overlay(tile_surface, size, center, radius, color, special)

    surface.blit(
        tile_surface,
        (rect.centerx - size // 2, rect.centery - size // 2),
        special_flags=pygame.BLEND_RGBA_ADD,
    )


def draw_special_overlay(surface, size, center, radius, color, special):
    if special == "row":
        neon_line(surface, (4, center[1]), (size - 4, center[1]), color)
    elif special == "col":
        neon_line(surface, (center[0], 4), (center[0], size - 4), color)
    elif special == "bomb":
        neon_circle(surface, center, radius * 1.15, color)
