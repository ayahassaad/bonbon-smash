import math

import pygame

SHAPES = ["circle", "diamond", "star", "square", "triangle", "hexagon"]


def lighten(color, amount=0.4):
    r, g, b = color
    return (
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
    )


def darken(color, amount=0.3):
    r, g, b = color
    return (
        int(r * (1 - amount)),
        int(g * (1 - amount)),
        int(b * (1 - amount)),
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
