import robinhood
import stockstream

non_pending_states = {'cancelled', 'failed', 'filled'}


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
        if order['state'] in non_pending_states or order['side'] == 'sell':
            continue
        price = order['limit']
        value += price * order['quantity']

    value += portfolio['cashBalance']

    return value


def compute_asset_stats(asset, portfolio_value, quote):
    shares = asset['shares']
    avg_cost = asset['avgCost']
    recent_price = robinhood.quote.most_recent_price(quote)

    dollar_change = recent_price - avg_cost
    percent_change = (dollar_change / avg_cost * 100)

    total_cost = shares * avg_cost
    total_value = shares * recent_price
    total_dollar_return = total_value - total_cost

    weight = (total_value / portfolio_value) * 100

    percent_change_today = robinhood.quote.percent_change_today(quote)

    return {
        'symbol': asset['symbol'],
        'shares': asset['shares'],
        'avg_cost': asset['avgCost'],
        'recent_price': recent_price,
        'dollar_change': dollar_change,
        'percent_change': percent_change,
        'total_cost': total_cost,
        'total_value': total_value,
        'total_dollar_return': total_dollar_return,
        'weight': weight,
        'percent_change_today': percent_change_today
    }


def compute_portfolio_statistics():
    portfolio = stockstream.api.get_current_portfolio()
    symbols = [asset['symbol'] for asset in portfolio['assets']]
    quote_map = robinhood.api.get_symbol_to_quotes(symbols)
    portfolio_value = compute_value(portfolio)

    asset_stats = {}

    for asset in portfolio['assets']:
        quote = quote_map[asset['symbol']]
        asset_stats[asset['symbol']] = compute_asset_stats(asset, portfolio_value, quote)

    return {
        "cash_balance": portfolio['cashBalance'],
        "asset_stats": asset_stats,
        "portfolio_value": portfolio_value
    }


def get_symbol_to_asset(portfolio):
    symbol_to_asset = {}
    for asset in portfolio['assets']:
        symbol_to_asset[asset['symbol']] = asset
    return symbol_to_asset
