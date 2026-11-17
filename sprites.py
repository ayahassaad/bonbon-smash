import math

import pygame

SHAPES = ["circle", "diamond", "star", "square", "triangle", "hexagon"]


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


def get_shape_points(shape, center, radius):
    if shape == "diamond":
        return regular_polygon_points(center, radius, 4, rotation=-math.pi / 4)
    if shape == "triangle":
        return regular_polygon_points(center, radius, 3, rotation=-math.pi / 2)
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

    if shape == "circle":
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, outline_color, center, radius, 2)
    elif shape == "square":
        side = radius * 1.6
        square_rect = pygame.Rect(0, 0, side, side)
        square_rect.center = center
        border_radius = int(side * 0.2)
        pygame.draw.rect(surface, color, square_rect, border_radius=border_radius)
        pygame.draw.rect(surface, outline_color, square_rect, width=2, border_radius=border_radius)
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
