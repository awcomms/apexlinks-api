def cdict(query, page=None, pages=None, **kwargs):
    items = [item.dict(**kwargs) for item in query]
    print('items', items)
    if 'run' in kwargs and kwargs['run']:
        run = kwargs['run']
        items = run(items)
    res =  {
        'items': items,
        'total': len(items)
    }
    if page:
        res['page'] = page
    if pages:
        res['pages'] = pages
    if 'extra' in kwargs:
        res.update(kwargs['extra'](items))
    return res