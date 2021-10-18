import math

def datetime_period(seconds, ly=False):
    seconds_in_minute = 60
    seconds_in_hour = seconds_in_minute*60
    seconds_in_day = seconds_in_hour*24
    seconds_in_week = seconds_in_day*7
    seconds_in_month = seconds_in_day*24
    seconds_in_year = seconds_in_day*365

    if math.floor(seconds/seconds_in_year) > 1:
        return 'yearly' if ly else 'year'
    elif math.floor(seconds/seconds_in_month) > 1:
        return 'monthly' if ly else 'month'
    elif math.floor(seconds/seconds_in_week) > 1:
        return 'weekly' if ly else 'week'
    elif math.floor(seconds/seconds_in_day) > 1:
        return 'daily' if ly else 'day'
    elif math.floor(seconds_in_hour) > 1:
        return 'hourly' if ly else 'hour'
    return 'always'