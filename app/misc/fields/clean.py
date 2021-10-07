def clean(field):
    if not field:
        field['label'] = field['label'].strip()
        field['value'] = field['value'].strip()
    return field