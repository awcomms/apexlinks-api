from fuzzywuzzy import process

def tag_sort(default_fields, items, tags):
    print('tag_sort')
    for item in items:
        item['score'] = 0
        if not isinstance(item['tags'], list):
            item['tags'] = []
        item_tags = item['tags']
        if 'user' in item:
            item_tags += item['user']['tags']
        if item['username']:
            item_tags.append(item['username'])
        if item['fields']:
            for field in item['fields']:
                if field['label'] in default_fields:
                    item_tags.append(field['value'])
        # if item['username'] == 'awcc': print(item_tags)
        for tag in tags:
            try:
                item['score'] += process.extractOne(
                    tag, item_tags)[1]
            except:
                continue
        # if fields and item['fields']:
        #     user.score += field_score(item['fields'], fields)

    print('b4s')     
    _sorted = sorted(items, key=lambda item: item['score'], reverse=True)
    return _sorted