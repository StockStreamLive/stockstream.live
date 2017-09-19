

def most_recent_price(quote):
    price = "0"
    if 'last_extended_hours_trade_price' in quote and quote['last_extended_hours_trade_price'] is not None:
        price = quote['last_extended_hours_trade_price']
    else:
        price = quote['last_trade_price']

    return float(price)


def percent_change_today(quote):
    recent_price = most_recent_price(quote)
    last_close = float(quote['previous_close'])
    change_today = recent_price - last_close
    change_today_percent = change_today / recent_price * 100
    return change_today_percent


def dollar_change_today(quote):
    recent_price = most_recent_price(quote)
    last_close = float(quote['previous_close'])
    change_today = recent_price - last_close
    return change_today
