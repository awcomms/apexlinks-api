def cdict(query, page=1, per_page=37, **kwargs):
    print('_query', query)
    items = [item.dict(**kwargs) for item in query]
    if 'run' in kwargs and kwargs['run']:
        run = kwargs['run']
        items = run(items)
    res =  {
        'items': items,
        # 'pages': resources.pages, TODO
        'total': len(items)
    }
    if 'extra' in kwargs:
        res.update(kwargs['extra'](items))
    return res