import robinhood
import stockstream


def compute_value(portfolio):
    value = 0

    symbols = [asset['symbol'] for asset in portfolio['assets']]

    quoteMap = robinhood.api.get_symbol_to_quotes(symbols)

    for asset in portfolio['assets']:
        symbol = asset['symbol']
        recent_price = robinhood.quote.most_recent_price(quoteMap[symbol])
        asset_value = recent_price * asset['shares']
        value += asset_value

    orders = stockstream.api.get_orders_today()

    for order in orders:
        if order['state'] == 'cancelled' or order['state'] == 'filled' or order['side'] == 'sell':
            continue
        price = order['limit']
        value += price * order['quantity']

    value += portfolio['cashBalance']

    return value


def get_symbol_to_asset(portfolio):
    symbol_to_asset = {}
    for asset in portfolio['assets']:
        symbol_to_asset[asset['symbol']] = asset
    return symbol_to_asset
