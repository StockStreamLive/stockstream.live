from datetime import datetime
from datetime import timedelta

import boto3

"""
start_date = "2017-05-30"
stop_date = "2013-05-01"

start = datetime.strptime(start_date, "%Y-%m-%d")
stop = datetime.strptime(stop_date, "%Y-%m-%d")

while start < stop:
    print start
    start = start + timedelta(days=1)
"""

import stockstream
from robinhood import robinhood_api


def find_order_for_vote(vote):
    symbol = vote['parameter']
    orders = stockstream.api.get_orders_by_date_by_symbol(vote['date'], symbol)
    buy_orders = [order for order in orders if order['side'] == 'buy']

    orders_by_timestamp = {}
    for order in buy_orders:
        orders_by_timestamp[order['timestamp']] = order

    if len(orders_by_timestamp) == 0:
        return None

    vote_timestamp = int(vote['timestamp'])

    closest = min(orders_by_timestamp, key=lambda x: abs(x - vote_timestamp))

    print `closest` + " - " + `vote_timestamp`

    print symbol + " -> " + `closest - vote_timestamp`



def find_voters_for_order(order, votes):
    if len(votes) == 0:
        print "Warning: No votes for order! " + `order`
        return []

    votes_by_timestamp = {}
    for vote in votes:
        if vote['action'].lower() != order['side'].lower():
            continue

        vote_timestamp = int(vote['timestamp'])
        if vote_timestamp not in votes_by_timestamp:
            votes_by_timestamp[vote_timestamp] = []
        votes_by_timestamp[vote_timestamp].append(vote)

    order_timestamp = order['timestamp']

    filtered = filter(lambda timestamp: timestamp < order_timestamp + 60000 and timestamp > order_timestamp - 10000000,
                      votes_by_timestamp)

    if len(filtered) == 0:
        print "Warning: No votes for order! " + `order`
        return None

    closest = min(filtered, key=lambda x: abs(x - order_timestamp))

    resp_voters = votes_by_timestamp[closest]

    votetimestr = datetime.fromtimestamp(closest / 1000).strftime('%Y-%m-%d %H:%M:%S')
    ordertimestr = datetime.fromtimestamp(order_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
    print `len(resp_voters)` + " users voted to " + order['side'] + " " + order[
        'symbol'] + " at " + votetimestr + " order placed at " + ordertimestr
    voters = [voter['username'] for voter in resp_voters]
    print voters

    return resp_voters


def find_voters_for_orders(date):
    orders = stockstream.api.get_orders_by_date(date)

    if len(orders) == 0:
        return

    votes = stockstream.api.get_votes_by_date(date)

    updates = []

    for order in orders:
        if order['state'] != "filled":
            continue

        filtered_votes = [vote for vote in votes if vote['parameter'] == order['symbol']]
        resp_votes = find_voters_for_order(order, filtered_votes)

        if not resp_votes:
            print "No voters for order " + `order`
            continue

        for vote in resp_votes:
            vote['orderId'] = order['id']

        updates += resp_votes

    return updates
    #open("ocache/" + date, "w").write(json.dumps(updates))



dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def processVotes(votes):
    table = dynamodb.Table('PlayerVotesProd')

    for vote in votes:
        print vote
        # response = table.delete_item(Key={'platform_username': vote['platform_username'],'timestamp': vote['timestamp']})
        # response = table.delete_item(Item=vote)
        # response = table.update_item(Item=vote)
        response = table.update_item(
            Key={'platform_username': vote['username'], 'timestamp': vote['timestamp']},
            UpdateExpression="set orderId = :id",
            ExpressionAttributeValues={':id': vote['orderId']},
            ReturnValues="UPDATED_NEW"
        )
        print response


if __name__ == "__main__":
    start_date = "06-03-2017"
    stop_date = "08-18-2017"

    start = datetime.strptime(start_date, "%m-%d-%Y")
    stop = datetime.strptime(stop_date, "%m-%d-%Y")

    while start < stop:
        datestr = str(start.strftime("%m-%d-%Y"))
        updates = find_voters_for_orders(datestr)
        if updates is not None:
            processVotes(updates)
        print datestr
        start = start + timedelta(days=1)

        #
# votes = stockstream.get_votes_by_symbol("SGYP")
