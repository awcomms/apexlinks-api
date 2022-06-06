FieldException = Exception()

def check(field):
    if not isinstance(field, dict):
        return f'let field {field} be of an object type'
    if not 'label' in field:
        return f'let field {field} have a label property'
    if not 'value' in field:
        return f'let field {field} have a value property'
    if not isinstance(field['label'], str):
        return f'let {field} label property be of a string type'
    if not isinstance(field['value'], str):
        return f'let {field} value property be of a string type'
    return