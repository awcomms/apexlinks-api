def cdict(query, page=1, per_page=37):
        resources = query.paginate(page, per_page, False)
        return {
            'items': [item.dict() for item in resources.items],
            'pages': resources.pages,
            'total': resources.total
        }