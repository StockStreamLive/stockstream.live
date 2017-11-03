import stockstream
import robinhood
from calendar import timegm
from dateutil.parser import parse


def compute_change_decimal(from_value, to_value):
    if from_value == 0 and to_value == 0:
        return 0
    from_value = 1 if from_value == 0 else from_value
    difference = (to_value - from_value)
    decimal_change = (difference / from_value)
    return decimal_change


def compute_cost(order):
    if 'average_price' in order and order['average_price'] is not None:
        return float(order['average_price'])
    return float(order['price'])


def organize_positions(positions, symbol_to_quote):

    influenced_orders = {
        "open": [],
        "closed": []
    }

    for position in positions:

        influence = position['influence']
        if influence == "Infinity":
            influence = 0

        buy_order = position['buyOrder']
        liable_players = position['liablePlayers']
        symbol = buy_order['symbol']
        buy_time = stockstream.order.find_execution_timestamp_for_order(buy_order)
        buy_price = compute_cost(buy_order)

        if 'sellOrder' not in position or position['sellOrder'] is None:

            quote = symbol_to_quote.get(symbol)

            if quote is None:
                continue

            recent_price = robinhood.quote.most_recent_price(quote)
            difference = (recent_price - buy_price)
            percent_change = compute_change_decimal(buy_price, recent_price) * 100
            liability = difference * influence

            timestamp = parse(buy_order['created_at'])
            timestamp = timegm(timestamp.timetuple()) * 1000

            influenced_orders['open'].append({
                "symbol": symbol,
                "buy_time": timestamp,
                "buy_price": buy_price,
                "recent_price": recent_price,
                "difference": difference,
                "percent_change": percent_change,
                "influence": influence,
                "liability": liability,
                "quote": quote,
                "liable_players": liable_players
            })

        else:
            sell_order = position['sellOrder']
            sell_price = compute_cost(sell_order)

            difference = sell_price - buy_price
            percent_change = compute_change_decimal(buy_price, sell_price) * 100
            sell_time = stockstream.order.find_execution_timestamp_for_order(sell_order)
            liability = influence * difference

            influenced_orders['closed'].append({
                "symbol": symbol,
                "buy_time": buy_time,
                "sell_time": sell_time,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "difference": difference,
                "percent_change": percent_change,
                "liability": liability,
                "influence": influence,
                "liable_players": liable_players
            })

    influenced_orders['closed'] = list(reversed(influenced_orders['closed']))

    return influenced_orders


def assemble_positions(positions):
    symbols = set([position['buyOrder']['symbol'] for position in positions])

    symbol_to_quote = robinhood.api.get_symbol_to_quotes(symbols)

    influenced_orders = stockstream.positions.organize_positions(positions, symbol_to_quote)
    profile_statistics = stockstream.positions.get_profile_statistics(influenced_orders)

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

        realized_liability += float(order['liability'])
        realized_buy_price += float(order['buy_price']) * order['influence']
        realized_sell_price += float(order['sell_price']) * order['influence']

    for order in influenced_orders['open']:
        if order['liability'] > 0:
            profitable_trades += 1
        else:
            unprofitable_trades += 1

        unrealized_return += order['liability']
        unrealized_buy_price += float(order['buy_price']) * order['influence']
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
