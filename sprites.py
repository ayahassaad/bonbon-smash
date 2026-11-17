import math

import pygame

from constants import BACKGROUND_COLOR

SHAPES = ["circle", "diamond", "star", "ring", "moon", "hexagon"]


def darken(color, amount=0.3):
    r, g, b = color
    return (
        int(r * (1 - amount)),
        int(g * (1 - amount)),
        int(b * (1 - amount)),
    )


def lighten(color, amount=0.4):
    r, g, b = color
    return (
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
    )


def regular_polygon_points(center, radius, sides, rotation=0.0):
    cx, cy = center
    points = []
    for i in range(sides):
        angle = rotation + i * (2 * math.pi / sides)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def star_points(center, outer_radius, inner_radius, rotation=-math.pi / 2):
    cx, cy = center
    points = []
    for i in range(10):
        angle = rotation + i * (math.pi / 5)
        radius = outer_radius if i % 2 == 0 else inner_radius
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


_glow_cache = {}


def get_glow_surface(color, radius):
    key = (color, round(radius))
    if key in _glow_cache:
        return _glow_cache[key]

    size = int(radius * 4)
    glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    glow_center = (size // 2, size // 2)
    layers = [(radius * 2.0, 16), (radius * 1.5, 30), (radius * 1.1, 55)]
    for layer_radius, alpha in layers:
        pygame.draw.circle(glow_surface, (*color, alpha), glow_center, layer_radius)

    _glow_cache[key] = glow_surface
    return glow_surface


def draw_glow(surface, center, color, radius):
    glow_surface = get_glow_surface(color, radius)
    size = glow_surface.get_width()
    surface.blit(
        glow_surface,
        (center[0] - size // 2, center[1] - size // 2),
        special_flags=pygame.BLEND_RGBA_ADD,
    )


def get_shape_points(shape, center, radius):
    if shape == "diamond":
        return regular_polygon_points(center, radius, 4, rotation=-math.pi / 4)
    if shape == "hexagon":
        return regular_polygon_points(center, radius, 6)
    if shape == "star":
        return star_points(center, radius, radius * 0.45)
    return None


def draw_candy(surface, rect, color_index, color, special=None):
    shape = SHAPES[color_index % len(SHAPES)]
    center = rect.center
    radius = rect.width * 0.38
    outline_color = darken(color, 0.35)

    draw_glow(surface, center, color, radius)

    if shape == "circle":
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, outline_color, center, radius, 2)
    elif shape == "ring":
        body_radius = radius * 0.65
        pygame.draw.circle(surface, color, center, body_radius)
        pygame.draw.circle(surface, outline_color, center, body_radius, 2)
        ring_rect = pygame.Rect(0, 0, radius * 2.1, radius * 0.75)
        ring_rect.center = center
        pygame.draw.ellipse(surface, lighten(color, 0.3), ring_rect, 3)
    elif shape == "moon":
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, outline_color, center, radius, 2)
        cutout_center = (center[0] + radius * 0.5, center[1] - radius * 0.15)
        pygame.draw.circle(surface, BACKGROUND_COLOR, cutout_center, radius * 0.85)
    else:
        points = get_shape_points(shape, center, radius)
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, outline_color, points, 2)

    draw_special_overlay(surface, rect, center, radius, color, special)


def draw_special_overlay(surface, rect, center, radius, color, special):
    stripe_color = lighten(color, 0.55)

    if special == "row":
        stripe_height = rect.height * 0.22
        stripe_rect = pygame.Rect(rect.left + 4, center[1] - stripe_height / 2, rect.width - 8, stripe_height)
        pygame.draw.rect(surface, stripe_color, stripe_rect, border_radius=int(stripe_height / 2))
    elif special == "col":
        stripe_width = rect.width * 0.22
        stripe_rect = pygame.Rect(center[0] - stripe_width / 2, rect.top + 4, stripe_width, rect.height - 8)
        pygame.draw.rect(surface, stripe_color, stripe_rect, border_radius=int(stripe_width / 2))
    elif special == "bomb":
        pygame.draw.circle(surface, (255, 255, 255), center, radius * 0.65, 3)
        pygame.draw.circle(surface, (255, 255, 255), center, radius * 0.32, 2)
