import json
import os

from constants import SAVE_PATH

LEVELS = [
    {"rows": 6, "cols": 6, "colors": 4, "target_score": 400, "move_limit": 14},
    {"rows": 6, "cols": 6, "colors": 4, "target_score": 600, "move_limit": 14},
    {"rows": 7, "cols": 7, "colors": 5, "target_score": 900, "move_limit": 16},
    {"rows": 7, "cols": 7, "colors": 5, "target_score": 1300, "move_limit": 16},
    {"rows": 8, "cols": 8, "colors": 5, "target_score": 1800, "move_limit": 18},
    {"rows": 8, "cols": 8, "colors": 6, "target_score": 2400, "move_limit": 18},
    {"rows": 8, "cols": 8, "colors": 6, "target_score": 3000, "move_limit": 20},
    {"rows": 9, "cols": 9, "colors": 6, "target_score": 3800, "move_limit": 22},
    {"rows": 9, "cols": 9, "colors": 6, "target_score": 4600, "move_limit": 22},
    {"rows": 10, "cols": 10, "colors": 6, "target_score": 6000, "move_limit": 26},
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
