from fuzzywuzzy import process
from app.misc import hasget
from app.misc.exceptions import ContinueI

continue_i = ContinueI()

def is_not_in(arr, obj):
    return obj and obj not in arr

def tag_sort(items, tags, include_user=False):  
    field_tags = [t for t in tags if hasget(t, 'field')]
    for idx, item in enumerate(items):
        item['score'] = 0
        if not 'tags' in item:
            return
        if not isinstance(item['tags'], list):
            item['tags'] = []
        item_tags = item['tags']
        if include_user and hasget(item, 'user') and item['user']['tags'] and type(item['user']['tags'] == list):
            item_tags += item['user']['tags']
        if 'username' in item:
            item_tags.append({'value': item['username']})
        try:
            item_tags_values = [hasget(i, 'value') for i in item_tags]
            item_field_tags = [t for t in item_tags if hasget(t, 'field')]
            field_tags_labels = [hasget(tag, 'label') for tag in field_tags]
            field_tags_values = [hasget(tag, 'value') for tag in field_tags]
            for tag in item_field_tags:
                if not hasget(tag, 'exact'): continue
                tag_label = hasget(tag, 'label')
                tag_value = hasget(tag, 'value')
                if is_not_in(field_tags_labels, tag_label) or is_not_in(field_tags_values, tag_value):
                    items.pop(idx)
                    raise continue_i
            for tag in tags:
                if hasget(tag, 'exact'):
                    if tag['value'] not in item_tags_values:
                        items.pop(idx)
                        raise continue_i
                try:
                    item['score'] += process.extractOne(
                        hasget(tag, 'value'), item_tags_values)[1]
                except:
                    continue
        except ContinueI:
            continue
    _sorted = sorted(items, key=lambda item: item['score'], reverse=True)
    return _sorted