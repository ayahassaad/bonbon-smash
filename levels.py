import json
import os

from constants import SAVE_PATH

LEVELS = [
    {"target_score": 500, "move_limit": 15},
    {"target_score": 800, "move_limit": 15},
    {"target_score": 1200, "move_limit": 18},
    {"target_score": 1600, "move_limit": 18},
    {"target_score": 2200, "move_limit": 20},
    {"target_score": 2800, "move_limit": 20},
    {"target_score": 3500, "move_limit": 22},
    {"target_score": 4200, "move_limit": 22},
    {"target_score": 5000, "move_limit": 25},
    {"target_score": 6000, "move_limit": 25},
]


def load_unlocked_level():
    if not os.path.exists(SAVE_PATH):
        return 0
    try:
        with open(SAVE_PATH) as f:
            data = json.load(f)
        return data.get("unlocked_level", 0)
    except (json.JSONDecodeError, OSError):
        return 0


def save_unlocked_level(unlocked_level):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump({"unlocked_level": unlocked_level}, f)
    except OSError:
        pass
