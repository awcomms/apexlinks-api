import re
from geopy import distance as dist

email_regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

def check_email(email):
    if(re.search(email_regex, email)):
        return True
    else:
        return False

def distance(one, two):
    return dist.distance(one, two)