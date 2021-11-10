from fuzzywuzzy import fuzz

def field_score(obj_fields, fields):
    obj_score = 0
    for field in fields:
        max = 0
        for obj_field in obj_fields:
            label_score = fuzz.ratio(
                field['label'], obj_field['label']
            )
            value_score = fuzz.ratio(
                field['value'], obj_field['value']
            )
            score = label_score + value_score
            if score > max:
                max = score
        obj_score += max
    return obj_score