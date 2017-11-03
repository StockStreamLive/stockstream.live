import requests
import httputil
import traceback
from datetime import datetime, timedelta


def get_symbol_to_quotes(symbols):
    if len(symbols) == 0:
        return {}
    symbol_to_quote = {}
    try:
        quotes = httputil.get_json_object_from_url("https://api.robinhood.com/quotes/?symbols={}".format(",".join(symbols)))['results']
        for quote in quotes:
            if quote:
                symbol_to_quote[quote['symbol']] = quote
    except Exception as e:
        traceback.print_exc()
        print "ERROR: " + `e`
    return symbol_to_quote


def get_market_hours(date):
    market_date = httputil.get_json_object_from_url("https://api.robinhood.com/markets/XNAS/hours/{}/".format(date))
    return market_date


def find_last_market_open_date():
    date_str = datetime.today().strftime('%Y-%m-%d')

    start = datetime.strptime(date_str, "%Y-%m-%d")

    while True:
        market_hours = get_market_hours(start.strftime('%Y-%m-%d'))
        if market_hours['is_open']:
            return start.strftime('%Y-%m-%d')
        start = start - timedelta(days=1)


def get_fundamentals(symbol):
    fundamentals = httputil.get_json_object_from_url("https://api.robinhood.com/fundamentals/{}/".format(symbol))
    return fundamentals


def get_quote(symbol):
    return httputil.get_json_object_from_url("https://api.robinhood.com/quotes/{}/".format(symbol))


def get_instrument_for_symbol(symbol):
    symbol_to_quote = get_symbol_to_quotes([symbol])
    quote = symbol_to_quote[symbol]
    return requests.get(quote["instrument"]).json()



