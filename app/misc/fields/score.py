from fuzzywuzzy import fuzz
from app.misc import hasget

def score(obj_fields, fields):
    obj_score = 0
    for field in fields:
        max = 0
        for obj_field in obj_fields:
            label_score = fuzz.ratio(
                hasget(field, 'label'), hasget(obj_field, 'label')
            )
            value_score = fuzz.ratio(
                hasget(field, 'value'), hasget(obj_field, 'value')
            )
            score = label_score + value_score
            if score > max:
                max = score
        obj_score += max
    return obj_score