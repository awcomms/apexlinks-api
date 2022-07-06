import json

def check_include(include, arg='query arg'):
    if not include:
        return
    type_error = {
        'error': f'let {arg} include be a JSON list of strings as a string'}, 400
    if isinstance(arg, str):
        try:
            include = json.loads(include)
        except TypeError or json.decoder.JSONDecodeError:
            raise Exception(type_error)
        except Exception as e:
            raise Exception(({'error': f'internal error while trying to parse {arg} include'}, 400))
    if not isinstance(include, list):
        raise Exception(type_error)
    return include