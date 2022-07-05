def cdict(query, page=None, per_page=37, **kwargs):
    items = [item.dict(**kwargs) for item in query]
    if 'run' in kwargs and kwargs['run']:
        run = kwargs['run']
        items = run(items)

    # slice items with step as `per_page`
    # get item at index `page-1`
    # get `per_page` number of items from item including item

    pages = None
    
    page_items = items
    items_length = len(items)
    if items_length > per_page:
        sliced = items[None:None:per_page]
        pages = len(sliced)

        if page == 'last':
            page = pages

        if page > pages:
            return {'error': f'specified page {page} more than available pages for query', 'pages': pages}


        first_in_page = sliced[page-1]
        print('fip', first_in_page)
        awid = [i for i in items if first_in_page['id'] == i['id']]
        print('awid', awid)
        index_of_first_in_page = items.index(
            awid[0])
        print('ifip', index_of_first_in_page)

        page_items = []
        for i in range(index_of_first_in_page, index_of_first_in_page + per_page):
            if i < items_length:
                page_items.append(items[i])

    res = {
        'items': page_items,
        'total': items_length
    }
    if page:
        res['page'] = page
    if pages:
        res['pages'] = pages
    if 'extra' in kwargs:
        res.update(kwargs['extra'](items))
    return res
