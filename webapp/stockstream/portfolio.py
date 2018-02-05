import robinhood
import stockstream

non_pending_states = {'cancelled', 'failed', 'filled'}


def compute_value(assets, quote_map):
    value = 0

    for asset in assets:
        symbol = asset['symbol']
        if symbol not in quote_map:
            continue
        recent_price = robinhood.quote.most_recent_price(quote_map[symbol])
        asset_value = recent_price * asset['shares']
        value += asset_value

    orders = stockstream.api.get_orders_today()

    for order in orders:
        if order['state'] in non_pending_states or order['side'] == 'sell':
            continue
        price = float(order['price'])
        value += price * int(float(order['quantity']))

    return value


def compute_asset_stats(asset, portfolio_value, quote_map):
    quote = quote_map[asset['symbol']]
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

    position_stats = stockstream.positions.assemble_positions_with_quotes(asset['positions'], quote_map)

    return {
        'symbol': asset['symbol'],
        'shares': asset['shares'],
        'position_stats': position_stats,
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


def construct_positions_map(positions):
    symbol_to_positions = {}
    for position in positions:
        symbol = position['buyOrder']['symbol']
        if symbol not in symbol_to_positions:
            symbol_to_positions[symbol] = []
        symbol_to_positions[symbol].append(position)

    return symbol_to_positions


def construct_asset(symbol, symbol_positions):
    totalshares = 0
    totalcost = 0

    for position in symbol_positions:
        buy_order = position['buyOrder']
        shares = int(float(buy_order['quantity']))

        totalcost += shares * float(buy_order['average_price'])
        totalshares += shares

    avgcost = totalcost / totalshares

    return {"symbol": symbol, "avgCost": avgcost, "shares": totalshares, "positions": symbol_positions}


def construct_assets(positions):
    symbol_to_positions = construct_positions_map(positions)

    assets = []

    for symbol in symbol_to_positions:
        assets.append(construct_asset(symbol, symbol_to_positions[symbol]))

    return assets


def compute_portfolio_statistics():

    positions = stockstream.api.get_open_positions()
    assets = construct_assets(positions)

    symbols = set([order['buyOrder']['symbol'] for order in positions])
    quote_map = robinhood.api.get_symbol_to_quotes(symbols)
    portfolio_value = compute_value(assets, quote_map)

    asset_stats = {}

    for asset in assets:
        if asset['symbol'] not in quote_map:
            continue
        asset_stats[asset['symbol']] = compute_asset_stats(asset, portfolio_value, quote_map)

    return {
        "cash_balance": 0,
        "total_value": portfolio_value,
        "asset_stats": asset_stats,
        "portfolio_value": portfolio_value
    }


def get_symbol_to_asset():
    positions = stockstream.api.get_open_positions()
    assets = construct_assets(positions)

    symbol_to_asset = {}
    for asset in assets:
        symbol_to_asset[asset['symbol']] = asset
    return symbol_to_asset
