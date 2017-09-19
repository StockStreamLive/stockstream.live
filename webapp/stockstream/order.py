import time
import pytz
from calendar import timegm
from dateutil.parser import parse


def find_execution_timestamp_for_order(order):
    timestamp = int(order['timestamp'])
    if 'executions' in order and order['executions'] is not None:
        timestamp = parse(order['executions'][0]['timestamp'])
        timestamp = timestamp.replace(tzinfo=pytz.utc)
        timestamp = timegm(timestamp.timetuple()) * 1000
    return timestamp


def find_sell_order_for_buy_order(buy_order):
    pass

