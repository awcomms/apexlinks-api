def cdict(query, page=None, per_page=37, **kwargs):
    items = [item.dict(**kwargs) for item in query]
    if 'run' in kwargs and kwargs['run']:
        run = kwargs['run']
        items = run(items)

    # slice items with step as `per_page`
    # get item at index `page-1`
    # get `per_page` number of items from item including item
    page_items = items
    if len(items) > per_page:
        sliced = items[None:None:per_page]
        pages = len(sliced)
        if page == 'last':
            page = pages
        first_in_page = sliced[page-1]
        index_of_first_in_page = items.index([i for i in items if first_in_page['id'] == i['id']][0])

        page_items = []
        for i in range(index_of_first_in_page, index_of_first_in_page + per_page):
            page_items.append(items[i])

    res =  {
        'items': page_items,
        'total': len(items)
    }
    if page:
        res['page'] = page
    if pages:
        res['pages'] = pages
    if 'extra' in kwargs:
        res.update(kwargs['extra'](items))
    return res