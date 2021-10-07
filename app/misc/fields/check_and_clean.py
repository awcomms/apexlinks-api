from .check import check
from .clean import clean

def check_and_clean(field):
    error = check(field)
    if error:
        return error
    return clean(field)