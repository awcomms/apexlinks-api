from geopy import distance

def cdict(query, page=1, per_page=10):
        resources = query.paginate(page, per_page, False)
        data = {
            'groups': [group.dict() for group in resources.groups],
            'pages': resources.pages,
            'total': resources.total}
        return data


def dist(p1, p2):
    return distance.distance(p1, p2)
