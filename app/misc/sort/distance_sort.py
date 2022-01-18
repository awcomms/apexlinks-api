from app.misc import hasget
from app.misc.distance import distance
from flask import current_app

def distance_sort(items, loc):
    target_lat = hasget(loc, 'lat')
    if not target_lat:
        current_app.logger.error('"lat" missing in distance_sort "loc" arg')
        return items
    
    target_lon = hasget(loc, 'lon')
    if not target_lat:
        current_app.logger.error('"lon" missing in distance_sort "loc" arg')
        return items
    
    target = (target_lat, target_lon)
    
    for idx, item in enumerate(items):
        item_location = hasget(item, 'location')
        if not item_location:
            continue

        lat = hasget(item_location, 'lat')
        if not lat:
            current_app.logger.error(f'"lat" missing in obj {idx} (item) in distance_sort "items" arg')
            continue
        
        lon = hasget(item_location, 'lon')
        if not lon:
            current_app.logger.error(
                f'"lat" missing in obj {idx} (item) in distance_sort "items" arg')
            continue

        location = (lat, lon)

        item['score'] = distance(location, target).kilometers
    return sorted(items, key=lambda item: item['score'])