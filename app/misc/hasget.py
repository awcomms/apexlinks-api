from typing import Any


def hasget(obj: Any, attr: str, default: Any=None):
    if obj:
        if attr in obj:
            return obj[attr]
    return default
