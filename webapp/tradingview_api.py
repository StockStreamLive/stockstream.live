

markets = {
    "https://api.robinhood.com/markets/ARCX/": "AMEX",
    "https://api.robinhood.com/markets/XASE/": "AMEX",
    "https://api.robinhood.com/markets/BATS/": "AMEX",
    "https://api.robinhood.com/markets/XNAS/": "NASDAQ",
    "https://api.robinhood.com/markets/XNYS/": "NYSE"
}


def get_market_for_instrument(instrument):
    return markets[instrument['market']]
