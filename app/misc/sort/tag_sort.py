from fuzzywuzzy import process
from app.misc.exceptions import ContinueI

continue_i = ContinueI()

def tag_sort(items, tags, include_user=False):  
    for idx, item in enumerate(items):
        item['score'] = 0
        if not 'tags' in item:
            return
        if not isinstance(item['tags'], list):
            item['tags'] = []
        item_tags = item['tags']
        if include_user and 'user' in item and item['user'] and item['user']['tags'] and type(item['user']['tags'] == list):
            item_tags += item['user']['tags']
        if 'username' in item:
            item_tags.append({'value': item['username']})
        if 'fields' in item and item['fields']:
            for field in item['fields']:
                item_tags.append(
                    {'value': f'{field["label"]}:{field["value"]}'})
        try:
            # item_tags_values = [i['value'] for i in item_tags]
            item_tags_values = []
            for tag in tags:
                if 'exact' in tag and tag['exact']:
                    if tag['value'] not in item_tags_values:
                        items.pop(idx)
                        raise continue_i
                try:
                    item['score'] += process.extractOne(
                        tag['value'], item_tags_values)[1]
                except:
                    continue
        except ContinueI:
            continue
    _sorted = sorted(items, key=lambda item: item['score'], reverse=True)
    return _sorted