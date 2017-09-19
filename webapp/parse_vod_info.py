import sys
import json
import datetime
import stockstream
import os

records = []

i = 0
files = os.listdir("rechat")
for f in files:
    """if i < 3:
        i += 1
        continue"""
    records += json.loads(open("rechat/" + f).read())
    print "Loaded {} now have {} records.".format(f, len(records))
    i += 1
    if i > 10:
        pass#break

date_to_votes = {}

for record in records:
    if 'attributes' not in record:
        continue

    timestamp = record['attributes']['timestamp']
    from_user = record['attributes']['from']
    message = record['attributes']['message'].encode('utf-8').lstrip().rstrip()

    if not message.startswith("!buy ") and not message.startswith("!sell "):
        continue

    fields = message.split(" ")

    if len(fields) != 2:
        continue

    action = fields[0][1:].upper()
    parameter = fields[1].upper()

    time_str = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%m-%d-%Y %H:%M:%S')
    date_str = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%m-%d-%Y')

    # print "{} {}: {}".format(time_str, from_user, message)

    if date_str not in date_to_votes:
        date_to_votes[date_str] = []

    date_to_votes[date_str].append({
        "username": "twitch:" + from_user,
        "action": action,
        "parameter": parameter,
        "timestamp": timestamp
    })

    #print "{} entries in date_to_votes.".format(len(date_to_votes))

date_to_objects = {}

total_orders = 0

order_id_to_order = {}

for date in date_to_votes:
    orders = stockstream.api.get_orders_by_date(date)

    fixed_orders = []
    i = 0
    while i < len(orders) - 1:
        this_order = orders[i]
        next_order = orders[i + 1]
        same_side = next_order['side'].lower() == this_order['side'].lower()
        same_symbol = next_order['symbol'].lower() == this_order['symbol'].lower()
        if this_order['state'] == 'cancelled' and next_order['state'] == 'filled' and same_side and same_symbol:
            next_order['timestamp'] = this_order['timestamp']
            i += 2
            fixed_orders.append(next_order)
        else:
            fixed_orders.append(this_order)
            i += 1

    fixed_orders = [order for order in fixed_orders if order['state'] == 'filled']
    total_orders += len(fixed_orders)

    for order in fixed_orders:
        order_id_to_order[order['id']] = order

    votes = date_to_votes[date]

    print "{} - {} votes {} orders".format(date, len(votes), len(fixed_orders))

    objects = [] + fixed_orders + votes
    sorted_objects = sorted(objects, key=lambda k: k['timestamp'])
    date_to_objects[date] = sorted_objects


orphan_orders = 0
matched_orders = 0

order_to_votes = {}

for date in date_to_votes:

    player_to_vote = {}

    print "{} orphan orders.".format(orphan_orders)

    objects = date_to_objects[date]
    for obj in objects:
        if 'id' in obj:
            resp_votes = []
            for player in player_to_vote:
                votes = player_to_vote[player]
                for vote in votes:
                    if vote['action'].lower() == obj['side'].lower() and vote['parameter'].lower() == obj['symbol'].lower():
                        diff = obj['timestamp'] - vote['timestamp']
                        if diff > 0 and diff < 600000:
                            resp_votes.append(vote)
            if len(resp_votes) <= 0:
                orphan_orders += 1
                #print "For order {} have {} voters:\n{}.".format(obj, len(resp_votes), resp_votes)
            else:
                matched_orders += 1

            order_to_votes[obj['id']] = resp_votes

        else:
            if obj['username'] not in player_to_vote:
                player_to_vote[obj['username']] = []
            player_to_vote[obj['username']].append(obj)


"""for id in order_to_votes:
    order = order_id_to_order[id]
    votes = order_to_votes[id]
    for vote in votes:
        diff = abs(order['timestamp'] - vote['timestamp'])
        print diff"""

print "{} total orders.".format(total_orders)
print "{} orphan orders.".format(orphan_orders)
print "{} matched orders.".format(matched_orders)
print "{} success rate".format(matched_orders/float(total_orders))
