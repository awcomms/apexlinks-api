def hasget(obj, attr):
    if hasattr(obj, attr) and getattr(obj, attr):
        return getattr(obj, attr)
    else:
        return False