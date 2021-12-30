def cdict(query, page=1, per_page=37, *args):
    resources = query.paginate(page, per_page, False)
    items = [item.dict() for item in resources.items]
    run = args[0]
    items = run(items)
    return {
        'items': [item.dict() for item in resources.items],
        'pages': resources.pages,
        'total': resources.total
    }