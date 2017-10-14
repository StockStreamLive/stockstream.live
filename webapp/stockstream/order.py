import time
import pytz
from calendar import timegm
from dateutil.parser import parse


def find_execution_timestamp_for_order(order):
    timestamp = parse(order['created_at'])
    timestamp = timegm(timestamp.timetuple()) * 1000

    if 'executions' in order and order['executions'] is not None:
        timestamp = parse(order['executions'][0]['timestamp'])
        timestamp = timestamp.replace(tzinfo=pytz.utc)
        timestamp = timegm(timestamp.timetuple()) * 1000
    return timestamp


