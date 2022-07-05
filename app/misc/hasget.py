def hasget(obj, attr, default=None):
    if obj:
        if attr in obj and obj[attr]:
            return obj[attr]
    return default
