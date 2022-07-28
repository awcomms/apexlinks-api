from typing import Literal
from app.misc.hasget import hasget


def cdict(query, page:int|Literal['last']='last', per_page=37, include=[], limit=None, append=False, **kwargs):
    if 'tags' not in include:
        include.append('tags')
    items = [item.dict(include=include, **kwargs) for item in query]
    print(items)
    run = hasget(kwargs, 'run')
    if run:
        items = run(items)
    for i in items:
        if not 'tags' in include:
            if hasget(i, 'tags'):
                    del i['tags']
        if hasget(i, 'search_tags'):
            del i['search_tags']
        if hasget(i, 'score'):
            del i['score']

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
            return {'error': f'specified page {page} more than pages made available by {per_page} items per page. number of available pages is {pages}'}

        first_in_page = sliced[page-1]
        awid = [i for i in items if first_in_page['id'] == i['id']]
        index_of_first_in_page = items.index(awid[0])

        if append:
            range_end = items_length
        else:
            range_end = per_page

        page_items = []
        for i in range(index_of_first_in_page, index_of_first_in_page + range_end):
            page_items.append(items[i])
    else:
        page = 1

    res_items = page_items
    
    if limit:
        res_items = page_items[0:limit]

    res = {
        'items': res_items,
        'total': items_length,
        'page': page
    }
    print(res_items)
    if pages:
        res['pages'] = pages
    if 'extra' in kwargs:
        res.update(kwargs['extra'](items))
    return res
