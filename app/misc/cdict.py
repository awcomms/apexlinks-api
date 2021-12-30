def cdict(query, page=1, per_page=37, **kwargs):
    resources = query.paginate(page, per_page, False)
    items = [item.dict() for item in resources.items]
    if 'run' in kwargs:
        run = kwargs['run']
        items = run(items)
    res =  {
        'items': items,
        'pages': resources.pages,
        'total': resources.total
    }
    res.update(kwargs['extra'](items))
    return res