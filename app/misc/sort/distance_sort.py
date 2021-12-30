from app.misc.distance import distance

def distance_sort(items, loc):
    for item in items:
        if not 'location' in item:
            continue
        item_location = (item['location']['lat'], item['location']['lon'])
        loc = (loc['lat'], loc['lon'])
        item['score'] = distance(item_location, loc).kilometers
    return sorted(items, key=lambda item: item['score'])