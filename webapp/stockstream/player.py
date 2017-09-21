import stockstream
import robinhood


def compute_change_decimal(from_value, to_value):
    if from_value == 0 and to_value == 0:
        return 0
    from_value = max(1, from_value)
    difference = (to_value - from_value)
    percent_change = (difference / from_value)
    return percent_change


def organize_positions(positions, symbol_to_quote):

    influenced_orders = {
        "open": [],
        "closed": []
    }

    for position in positions:

        influence = position['influence']
        buy_order = position['buyOrder']
        symbol = buy_order['symbol']
        buy_time = stockstream.order.find_execution_timestamp_for_order(buy_order)

        if 'sellOrder' not in position or position['sellOrder'] is None:

            quote = symbol_to_quote.get(symbol)

            if quote is None:
                continue

            recent_price = robinhood.quote.most_recent_price(quote)
            difference = (recent_price - buy_order['price'])
            percent_change = compute_change_decimal(buy_order['price'], recent_price)
            liability = difference * influence

            influenced_orders['open'].append({
                "symbol": symbol,
                "buy_time": buy_order['timestamp'],
                "buy_price": buy_order['price'],
                "recent_price": recent_price,
                "difference": difference,
                "percent_change": percent_change,
                "influence": influence,
                "liability": liability,
                "quote": quote
            })

        else:
            sell_order = position['sellOrder']

            difference = sell_order['price'] - buy_order['price']
            percent_change = compute_change_decimal(buy_order['price'], sell_order['price'])
            sell_time = stockstream.order.find_execution_timestamp_for_order(sell_order)
            liability = influence * difference

            influenced_orders['closed'].append({
                "symbol": symbol,
                "buy_time": buy_time,
                "sell_time": sell_time,
                "buy_price": buy_order['price'],
                "sell_price": sell_order['price'],
                "difference": difference,
                "percent_change": percent_change,
                "liability": liability,
                "influence": influence
            })

    return influenced_orders


def compute_player_profile(username):
    positions = stockstream.api.get_positions_by_player(username)

    symbols = set([position['buyOrder']['symbol'] for position in positions])

    symbol_to_quote = robinhood.api.get_symbol_to_quotes(symbols)

    influenced_orders = stockstream.player.organize_positions(positions, symbol_to_quote)
    profile_statistics = stockstream.player.get_profile_statistics(influenced_orders)

    print "Got influenced orders"

    return {
        "influenced_orders": influenced_orders,
        "profile_statistics": profile_statistics
    }


def get_profile_statistics(influenced_orders):

    profitable_trades = 0
    unprofitable_trades = 0

    realized_liability = 0
    realized_buy_price = 0
    realized_sell_price = 0

    unrealized_return = 0
    unrealized_buy_price = 0
    unrealized_sell_price = 0

    for order in influenced_orders['closed']:
        if order['liability'] > 0:
            profitable_trades += 1
        else:
            unprofitable_trades += 1

        realized_liability += order['liability']
        realized_buy_price += order['buy_price'] * order['influence']
        realized_sell_price += order['sell_price'] * order['influence']

    for order in influenced_orders['open']:
        if order['liability'] > 0:
            profitable_trades += 1
        else:
            unprofitable_trades += 1

        unrealized_return += order['liability']
        unrealized_buy_price += order['buy_price'] * order['influence']
        unrealized_sell_price += order['recent_price'] * order['influence']

    total_open = len(influenced_orders['open'])
    total_closed = len(influenced_orders['closed'])
    total_influenced = total_open + total_closed

    realized_percent_return = compute_change_decimal(realized_buy_price, realized_sell_price) * 100
    unrealized_percent_return = compute_change_decimal(unrealized_buy_price, unrealized_sell_price) * 100

    total_return = unrealized_return + realized_liability

    total_buy_price = realized_buy_price + unrealized_buy_price
    total_sell_price = realized_sell_price + unrealized_sell_price

    total_percent_return = compute_change_decimal(total_buy_price, total_sell_price) * 100

    return {
        'total_open': total_open,
        'total_closed': total_closed,
        'total_influenced': total_influenced,

        'realized_return': realized_liability,
        'realized_buy_price': realized_buy_price,
        'realized_sell_price': realized_sell_price,
        'realized_percent_return': realized_percent_return,

        'unrealized_return': unrealized_return,
        'unrealized_buy_price': unrealized_buy_price,
        'unrealized_sell_price': unrealized_sell_price,
        'unrealized_percent_return': unrealized_percent_return,

        'profitable_trades': profitable_trades,
        'unprofitable_trades': unprofitable_trades,

        'total_return': total_return,
        'total_percent_return': total_percent_return,
        'total_buy_price': total_buy_price,
        'total_sell_price': total_sell_price
    }
