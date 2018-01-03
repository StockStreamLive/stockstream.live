from calendar import timegm
from dateutil.parser import parse
from datetime import datetime

def create_timestamp(date_str):
    timestamp = parse(date_str)
    timestamp = timegm(timestamp.timetuple()) * 1000
    return timestamp


def human_date(timestamp_ms):
    time_str = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%y-%m-%d %H:%M')
    return time_str


def id(str_value):
    return ''.join(e for e in str_value if e.isalnum())


def human_format(num):
    if num is None:
        return "-"

    if isinstance(num, basestring):
        num = float(num)

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B'][magnitude])


def decimal_value(num):
    if num is None:
        return "-"

    if isinstance(num, basestring):
        num = float(num)

    return "{:.2f}".format(num)


def dollar_value(num):
    if num is None:
        return "-"

    if isinstance(num, basestring):
        num = float(num)

    return "$" + "{:,.2f}".format(abs(num))


def percent_value(num):
    return "{:.2f}".format(abs(num)) + "%"


def dollar_change(num):
    return ("-" if num < 0 else "+") + dollar_value(num)


def percent_change(num):
    return ("-" if num < 0 else "+") + percent_value(num)
