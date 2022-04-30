def hasget(obj, attr):
    print('hasget', obj, attr)
    if attr in obj and obj[attr]:
        return obj[attr]
    else:
        return False