from app.misc.hasget import hasget

def check_tags(tags, a):
    if not isinstance(tags, list):
        return f'tags {a} is not a list'
    for idx, tag in enumerate(tags):
        try:
            if not hasget(tag, 'value'):
                return f'tag {a} at index {idx} does not seem to have a value field'
        except TypeError:
            return f'tag {a} at index {idx} does not seem to be a JSON object'
    return None