from typing import List
from app.misc.hasget import hasget
from app.misc.types.tag import Tag

def check_tags(tags, a: str):
    tag: Tag
    for idx, tag in enumerate(tags):
        try:
            if not hasget(tag, 'value'):
                return f'let item at index {idx} in {a} have a field `value`'
        except TypeError:
            return f'let item at index {idx} in {a} be a JSON object'
    return None