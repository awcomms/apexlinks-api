def hasget(obj, attr, default=None):
    if attr in obj and obj[attr]:
        return obj[attr]
    else:
        return default
