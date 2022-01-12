from fuzzywuzzy import process
from app.misc.exceptions import ContinueI

continue_i = ContinueI()

def tag_sort(default_fields, items, tags):
    for idx, item in enumerate(items):
        item['score'] = 0
        if not isinstance(item['tags'], list):
            item['tags'] = []
        item_tags = item['tags']
        if 'user' in item:
            item_tags += item['user']['tags']
        if 'username' in item:
            item_tags.append({'value': item['username']})
        if 'fields' in item:
            for field in item['fields']:
                if field['label'] in default_fields:
                    item_tags.append({'value': field['value']})
        try:
            for tag in tags:
                if tag['exact']:
                    if tag['value'] not in [i['value'] for i in item_tags]:
                        items.pop(idx)
                        raise continue_i
                try:
                    item['score'] += process.extractOne(
                        tag['value'], [i['value'] for i in item_tags])[1]
                except:
                    continue
        except ContinueI():
            continue
        # if fields and item['fields']:
        #     user.score += field_score(item['fields'], fields)

    _sorted = sorted(items, key=lambda item: item['score'], reverse=True)
    return _sorted