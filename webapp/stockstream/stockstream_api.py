import config
import robinhood
import time
import httputil
import s3util
import json


def get_profile_by_player(player):
    return json.loads(s3util.read_file_data("api.stockstream.live", "profile/" + player.replace(":", "/")))


def get_api_request(request):
    return httputil.get_json_object_from_url(config.SS_API_ENDPOINT + request)


def get_current_portfolio():
    portfolio = get_api_request("/v1/portfolio/current")
    return portfolio


def get_votes_by_symbol(symbol):
    request = "/v1/votes/symbol/{}".format(symbol)
    votes = get_api_request(request)
    return votes


def get_votes_by_orderId(orderId):
    request = "/v1/votes/order/{}".format(orderId)
    votes = get_api_request(request)
    return votes


def get_influence_for_player(username):
    request = "/v1/influence/player/{}".format(username)
    order_to_influence = get_api_request(request)
    return order_to_influence


def get_votes_by_order_ids(order_ids):
    order_to_votes = {}
    chunks = split_list(order_ids, 50)
    for chunk in chunks:
        request = "/v1/votes/orders?ids={}".format(",".join(chunk))
        id_to_votes = get_api_request(request)
        for id in id_to_votes:
            order_to_votes[id] = id_to_votes[id]
    return order_to_votes


def get_votes_today():
    today_str = time.strftime("%m-%d-%Y")
    return get_votes_by_date(today_str)


def get_votes_by_date(date):
    request = "/v1/votes/date/{}".format(date)
    votes = get_api_request(request)
    return votes


def get_votes_by_date_by_symbol(date, symbol):
    request = "/v1/votes/date/{}".format(date)
    votes = get_api_request(request)
    filtered = [vote for vote in votes if vote['parameter'] == symbol]
    return filtered


def voteStats(player):
    request = "/v1/votes/player/twitch:{}".format(player)
    votes = get_api_request(request)
    newvotes = sorted(votes, key=lambda k: k['timestamp'])
    return newvotes


def split_list(lst, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_orders_by_id(order_ids):
    all_orders = []
    chunks = split_list(order_ids, 50)
    for chunk in chunks:
        request = "/v1/orders?ids={}".format(",".join(chunk))
        votes = get_api_request(request)
        all_orders += votes
    orders = sorted(all_orders, key=lambda k: k['timestamp'])
    return orders


def get_orders_by_symbol(symbol):
    request = "/v1/orders/symbol/{}".format(symbol)
    orders = get_api_request(request)
    orders = sorted(orders, key=lambda k: k['timestamp'])
    return orders


def get_positions_by_player(username):
    request = "/v1/positions/player/{}".format(username)
    positions = get_api_request(request)
    return positions


def get_orders_by_player(username):
    request = "/v1/orders/player/{}".format(username)
    orders = get_api_request(request)
    orders = sorted(orders, key=lambda k: k['timestamp'])
    return orders


def get_orders_today():
    today_str = time.strftime("%m-%d-%Y")
    return get_orders_by_date(today_str)


def get_orders_by_date(dateStr):
    request = "/v1/orders/date/{}".format(dateStr.replace("/", "-"))
    votes = get_api_request(request)
    newvotes = sorted(votes, key=lambda k: k['timestamp'])
    return newvotes


def get_orders_by_date_by_symbol(dateStr, symbol):
    request = "/v1/orders/date/{}".format(dateStr.replace("/", "-"))
    orders = get_api_request(request)
    neworders = sorted(orders, key=lambda k: k['timestamp'])
    filtered = [order for order in neworders if order['symbol'] == symbol]
    return filtered


def get_votes_by_user(username):
    return get_api_request("/v1/votes/player/{}".format(username))


def get_portfolio():
    return get_api_request("/v1/portfolio/current")


def get_symbols_from_portfolio(portfolio):
    return [asset['symbol'] for asset in portfolio['assets']]


def get_net_worth(portfolio):
    symbols = get_symbols_from_portfolio(portfolio)
    symbol_to_quotes = robinhood.api.get_symbol_to_quotes(symbols)
    net_worth = portfolio['cashBalance']
    for asset in portfolio['assets']:
        symbol = asset['symbol']
        quote = symbol_to_quotes[symbol]
        net_worth += robinhood.quote.most_recent_price(quote) * asset['shares']
    return net_worth


def get_overview(portfolio):
    return {
        "start_value": 50000,
        "net_worth": get_net_worth(portfolio)
    }