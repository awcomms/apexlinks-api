from fuzzywuzzy import process, fuzz

def fuzlist(q, list):
    r = process.extractOne(q, list)[1]
    if r > 90:
        return True
    else:
        return False

def fuz(q, string):
    ratio = fuzz.ratio(q, string)
    return rati
    