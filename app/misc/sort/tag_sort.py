from fuzzywuzzy import process
from app.misc import hasget
from app.misc.exceptions import ContinueI
from app.misc.fields import score

continue_i = ContinueI()


def is_not_in(arr, obj):
    return obj and obj not in arr


def tag_sort(items, tags, include_user=False):
    # field_tags = [t for t in tags if hasget(t, 'field')]

    for item in items:
        if not 'tags' in item:
            item['tags'] = []
        if not isinstance(item['tags'], list):
            item['tags'] = []

    for tag in tags:
        if hasget(tag, 'exact'):
            items = [i for i in items if hasget(tag, 'value', '') in [hasget(t, 'value', '') for t in i['tags']]]
        for item in items:
            item['score'] = 0
            try:
                item['score'] += process.extractOne(
                    hasget(tag, 'value'), [hasget(t, 'value', '') for t in item['tags']])[1]
            except Exception as tpe:
                print(f'tag_sort exception. item: {item["id"]}, item_tags: {item["tags"]}. current tag: {tag}. exception:', tpe)
                continue

    # for idx, item in enumerate(items):
    #     item['score'] = 0

    #     if not 'tags' in item:
    #         item['tags'] = []
    #     if not isinstance(item['tags'], list):
    #         item['tags'] = []

    #     item_tags = item['tags']

    #     # if include_user and hasget(item, 'user') and hasget(item['user'], 'tags') and isinstance(item['user']['tags'], list):
    #     #     item_tags += item['user']['tags']

    #     # if 'username' in item:
    #     #     item_tags.append({'value': item['username']})

    #     item_tags_values = [hasget(i, 'value') for i in item_tags]

    #     # item_field_tags = [t for t in item_tags if hasget(t, 'field')]

    #     try:
    #         # for tag in item_field_tags:
    #         #     if hasget(tag, 'exact'):
    #         #         if len([t for t in 
    #         #                 [t for t in field_tags if hasget(t, 'label') == hasget(tag, 'label')]
    #         #                     if hasget(t, 'value') == hasget(tag, 'value')]) < 1:
    #         #             print('ret', tag)
    #         #             items.pop(idx)
    #         #             raise continue_i
    #         #     else:
    #         #         item['score'] += score(item_field_tags, field_tags)

    #         for tag in tags:
    #             # if hasget(tag, 'field'):
    #             #     continue
    #             # if hasget(tag, 'exact'):
    #             #     if tag['value'] not in item_tags_values:
    #             #         items.pop(idx)
    #             #         raise continue_i
    #             #     else:
    #             #         print(item['id'], item_tags)
    #             try:
    #                 item['score'] += process.extractOne(
    #                     hasget(tag, 'value'), item_tags_values)[1]
    #             except Exception as tpe:
    #                 print(f'tag_sort exception. item: {item["id"]}, item_tags: {item["tags"]}, item_tags_values: {item_tags_values}. current tag: {tag}. exception:', tpe)
    #                 continue
    #     except ContinueI:
    #         continue
    
    _sorted = sorted(items, key=lambda item: hasget(item, 'score', 0), reverse=True)

    return _sorted
