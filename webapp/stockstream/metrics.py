from datetime import date
import stockstream
import robinhood


def get_days_old():
    start_date = date(2017, 5, 30)
    now_date = date.today()
    delta = now_date - start_date
    days = delta.days
    return days


def compute_stats_for_symbol(symbol):
    orders = stockstream.api.get_orders_by_symbol(symbol)
    quote = robinhood.api.get_quote(symbol)
    recent_price = robinhood.quote.most_recent_price(quote)
    percent_change = robinhood.quote.percent_change_today(quote)
    dollar_change = robinhood.quote.dollar_change_today(quote)

    balance = 0
    buys = 0
    sells = 0
    trades = 0

    for order in orders:

        if not order['state'] == 'filled':
            continue

        price = order['price']
        shares = int(order['quantity'])

        trades = trades + 1

        if order['side'] == 'sell':
            balance += (price * shares)
            sells += shares
        else:
            buys += shares
            balance -= (price * shares)

    shares = buys - sells
    worth = shares * recent_price
    net = balance + worth

    stats = {
        "net": net,
        "bought": buys,
        "sold": sells,
        "recent_price": recent_price,
        "percent_change": percent_change,
        "dollar_change": dollar_change,
    }

    return stats
