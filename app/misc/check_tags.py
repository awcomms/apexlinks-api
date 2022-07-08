from app.misc.hasget import hasget

def check_tags(tags, a):
    if not isinstance(tags, list):
        return f'let {a} be a list'
    for idx, tag in enumerate(tags):
        try:
            if not hasget(tag, 'value'):
                return f'let value at index {idx} in {a} have a value field'
        except TypeError:
            return f'let value at index {idx} in {a} be a JSON object'
    return None