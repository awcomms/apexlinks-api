from .all_countries import data

def countries():
    return [{
        'text': c['name'],
        'name': c['name'],
        'id': c['iso3']
        } for c in data]

def allStates():
    states = []
    for country in data:
        for state in country['states']:
            states.append({
                'id': state['id'],
                'name': state['name'],
            })
    return states

def allCities():
    cities = []
    for country in data:
        for state in country['states']:
            for city in state['cities']:
                cities.append({
                    'id': str(state['id']) + '' + str(city['id']),
                    'name': city['name'],
                })
    return cities

def states(country):
    if country:
        print('is country')
        for entry in data:
            if entry['iso3'] == country:
                states = entry['states']
        if not country:
            return None
    else:
        states = allStates()
    return [{
        'id': s['id'],
        'text': s['name'],
        'name': s['name']
    } for s in states]

def cities(country_iso3, state_id):
    if country_iso3 and state_id:
        country = None
        state = None
        for entry in data:
            if entry['iso3'] == country_iso3:
                country = entry
        if not country:
            return {'error': f'country {country} not found'}
        for entry in country['states']:
            if entry['id'] == state_id:
                cities = entry['cities']
        if not state:
            return {'error': f'state {state} not found'}
    else:
        cities = allCities()
    return [{
        'id': c['id'],
        'text': c['name'],
        'name': c['name']
    } for c in cities]
