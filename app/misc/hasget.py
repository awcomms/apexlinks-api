def hasget(obj, attr, default=None):
    if obj:
        if attr in obj:
            return obj[attr]
    return default
