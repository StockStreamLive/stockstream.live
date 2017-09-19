import stockstream
import robinhood
import json

from operator import itemgetter


def organize_positions(positions, symbol_to_quote):
    total = 0

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

            price = robinhood.quote.most_recent_price(quote)
            difference = (price - buy_order['price'])
            mod = difference * influence

            influenced_orders['open'].append({
                "symbol": symbol,
                "buy_time": buy_order['timestamp'],
                "buy_price": buy_order['price'],
                "influence": influence,
                "recent_price": price,
                "quote": quote
            })

        else:
            sell_order = position['sellOrder']

            difference = sell_order['price'] - buy_order['price']

            sell_time = stockstream.order.find_execution_timestamp_for_order(sell_order)

            mod = influence * difference

            influenced_orders['closed'].append({
                "symbol": symbol,
                "buy_time": buy_time,
                "sell_time": sell_time,
                "buy_price": buy_order['price'],
                "sell_price": sell_order['price'],
                "influence": influence
            })

        total += mod

    return influenced_orders


def compute_player_profile(username):
    positions = stockstream.api.get_positions_by_player(username)

    symbols = set([position['buyOrder']['symbol'] for position in positions])

    symbol_to_quote = robinhood.api.get_symbol_to_quotes(symbols)

    influenced_orders = stockstream.player.organize_positions(positions, symbol_to_quote)

    print "Got influenced orders"

    return {
        "influenced_orders": influenced_orders
    }


def get_profile_statistics(profile):
    influenced_orders = profile['influenced_orders']

    total_influenced = len(influenced_orders['closed']) + len(influenced_orders['open'])

    profitable_trades = 0
    unprofitable_trades = 0

    realized_return = 0

    for order in influenced_orders['closed']:
        diff = order['sell_price'] - order['buy_price']
        mod = diff * order['influence']

        if mod > 0:
            profitable_trades += 1
        else:
            unprofitable_trades += 1

        realized_return += mod

    unrealized_return = 0

    for order in influenced_orders['open']:
        diff = order['recent_price'] - order['buy_price']
        mod = diff * order['influence']

        if mod > 0:
            profitable_trades += 1
        else:
            unprofitable_trades += 1

        unrealized_return += mod

    div = 1 if total_influenced == 0 else total_influenced
    average_return = (realized_return + unrealized_return) / float(div)

    return {
        'total_influenced': total_influenced,
        'profitable_trades': profitable_trades,
        'unprofitable_trades': unprofitable_trades,
        'realized_return': realized_return,
        'unrealized_return': unrealized_return,
        'average_return': average_return
    }


def get_player_overview(username):
    votes = stockstream.api.get_votes_by_user(username)

    buy_sell_stats = {"BUY": 0, "SELL": 0}
    symbol_to_buy_sell = {}
    votes_by_date = {}
    cmd_stats = {}
    symbol_stats = {}

    for vote in votes:
        symbol = vote['parameter']
        action = vote['action']
        cmd = action + " " + symbol
        date = vote['date']

        if cmd not in cmd_stats:
            cmd_stats[cmd] = 0

        if symbol not in symbol_stats:
            symbol_stats[symbol] = 0

        if date not in votes_by_date:
            votes_by_date[date] = {"BUY": 0, "SELL": 0}

        if symbol not in symbol_to_buy_sell:
            symbol_to_buy_sell[symbol] = {"BUY": 0, "SELL": 0}

        cmd_stats[cmd] += 1
        symbol_stats[symbol] += 1
        buy_sell_stats[action] += 1
        votes_by_date[date][action] += 1
        symbol_to_buy_sell[symbol][action] += 1

    sorted_cmds = sorted(cmd_stats.iteritems(), key=itemgetter(1), reverse=True)
    sorted_dates = sorted(votes_by_date.iteritems(), key=itemgetter(0), reverse=False)

    top_cmds = {}
    end = 10
    if len(sorted_cmds) < end:
        end = len(sorted_cmds) - 1

    while end >= 0:
        cmd = sorted_cmds[end]
        top_cmds[cmd[0]] = cmd[1]
        end -= 1

    other_stats = {}
    symbol_stats_filtered = {}
    for symbol in symbol_stats.keys():
        votes = symbol_stats[symbol]
        if votes <= 5:
            if "Other" not in symbol_stats_filtered:
                symbol_stats_filtered["Other"] = 0
            symbol_stats_filtered["Other"] += votes

            other_stats[symbol] = votes

        else:
            symbol_stats_filtered[symbol] = symbol_stats[symbol]

    return {
        "BUY": buy_sell_stats["BUY"],
        "SELL": buy_sell_stats["SELL"],
        "symbol_stats": symbol_stats_filtered,
        "other_stats": other_stats,
        "votes_list": sorted_dates,
        "symbol_to_buy_sell": json.dumps(symbol_to_buy_sell)
    }

