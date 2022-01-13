from fuzzywuzzy import process
from app.misc.exceptions import ContinueI

continue_i = ContinueI(Exception)

def tag_sort(items, tags):
    print('ze tags', tags)
    for idx, item in enumerate(items):
        item['score'] = 0
        if not 'tags' in item:
            return
        if not isinstance(item['tags'], list):
            item['tags'] = []
        item_tags = item['tags']
        if 'user' in item:
            item_tags += {'value': item['user']['tags']}
        if 'username' in item:
            item_tags.append({'value': item['username']})
        if 'fields' in item and item['fields']:
            for field in item['fields']:
                item_tags.append(
                    {'value': f'{field["label"]}:{field["value"]}'})
        try:
            item_tags_values = [i['value'] for i in item_tags]
            print(item_tags_values)
            for tag in tags:
                if 'exact' in tag and tag['exact']:
                    print('_exact')
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
        print('_i_tags', item['tags'])
        print('_score', item['score'])
    _sorted = sorted(items, key=lambda item: item['score'], reverse=True)
    return _sorted