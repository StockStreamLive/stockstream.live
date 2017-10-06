import requests
import httputil
import traceback


def get_symbol_to_quotes(symbols):
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


def get_fundamentals(symbol):
    fundamentals = httputil.get_json_object_from_url("https://api.robinhood.com/fundamentals/{}/".format(symbol))
    return fundamentals


def get_quote(symbol):
    return httputil.get_json_object_from_url("https://api.robinhood.com/quotes/{}/".format(symbol))


def get_instrument_for_symbol(symbol):
    symbol_to_quote = get_symbol_to_quotes([symbol])
    quote = symbol_to_quote[symbol]
    return requests.get(quote["instrument"]).json()



