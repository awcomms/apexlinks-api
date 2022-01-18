from fuzzywuzzy import process
from app.misc import hasget
from app.misc.exceptions import ContinueI
from app.misc.fields import score

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
            
        item_tags_values = [hasget(i, 'value') for i in item_tags]

        item_field_tags = [t for t in item_tags if hasget(t, 'field')]

        try:
            for tag in item_field_tags:
                if hasget(tag, 'exact'):
                    if len([t for t in [t for t in field_tags if hasget(
                        t, 'label') == hasget(tag, 'label')] if hasget(t, 'value') == hasget(tag, 'value')]) < 1:
                        items.pop(idx)
                        raise continue_i
                else:
                    item['score'] += score(item_field_tags, field_tags)
                    
            for tag in tags:
                if hasget(tag, 'field'): continue
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