import json
import os

from constants import SAVE_PATH

MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 12
MIN_COLORS = 4
MAX_COLORS = 6


def get_level(index):
    size = min(MIN_GRID_SIZE + index // 2, MAX_GRID_SIZE)
    colors = min(MIN_COLORS + index // 3, MAX_COLORS)
    move_limit = 12 + size + index // 2
    target_score = int(300 * (size - 3) * (1 + index * 0.18))
    return {
        "rows": size,
        "cols": size,
        "colors": colors,
        "target_score": target_score,
        "move_limit": move_limit,
    }


def _load_save():
    if not os.path.exists(SAVE_PATH):
        return {}
    try:
        with open(SAVE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f)
    except OSError:
        pass


def load_unlocked_level():
    return _load_save().get("unlocked_level", 0)


def save_unlocked_level(unlocked_level):
    data = _load_save()
    data["unlocked_level"] = unlocked_level
    _write_save(data)


def load_tutorial_seen():
    return _load_save().get("tutorial_seen", False)


def mark_tutorial_seen():
    data = _load_save()
    data["tutorial_seen"] = True
    _write_save(data)
