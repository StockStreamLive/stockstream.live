import sys
import json
import stockstream
import scheduler
from datetime import datetime
from datetime import timedelta

"""
player = "twitch:" + sys.argv[1]

profile = stockstream.api.get_profile_by_player(player)
influenced_orders = profile['influenced_orders']

realized_return = 0

for order in influenced_orders['closed']:
    symbol = order['symbol']
    buy_time = datetime.fromtimestamp(order['buy_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    sell_time = datetime.fromtimestamp(order['sell_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    diff = order['sell_price'] - order['buy_price']
    mod = diff * order['influence']

    print 'Bought {} for {} on {} then sold for {} on {} for a profit of ${} influence {} mod {}'.format(
        symbol, order['buy_price'], buy_time, order['sell_price'], sell_time, diff, order['influence'], mod)

    realized_return += mod


unrealized_return = 0


for order in influenced_orders['open']:
    symbol = order['symbol']
    buy_time = datetime.fromtimestamp(order['buy_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    diff = order['recent_price'] - order['buy_price']
    mod = diff * order['influence']

    print 'Bought {} for {} on {} and still holding with value {} and return of {} influence {} mod {}'.format(
        symbol, order['buy_price'], buy_time, order['recent_price'], diff, order['influence'], mod)

    unrealized_return += mod

print "Realized: $" + `realized_return`
print "Unrealized: $" + `unrealized_return`
print "Total Score: $" + `realized_return + unrealized_return`"""

from multiprocessing.dummy import Pool as ThreadPool


i = 0
def processUser(username):
    global i
    print i
    profile = stockstream.positions.assemble_positions(username)
    open("twitch/" + username.split(":")[1], "w").write(json.dumps(profile))
    i += 1


# function to be mapped over
def calculateParallel(users, threads=5):
    pool = ThreadPool(threads)
    results = pool.map(processUser, users)
    pool.close()
    pool.join()
    return results

players = set([])

start_date = "05-30-2017"
stop_date = "08-30-2017"

start = datetime.strptime(start_date, "%m-%d-%Y")
stop = datetime.strptime(stop_date, "%m-%d-%Y")

while start < stop:
    datestr = str(start.strftime("%m-%d-%Y"))
    votes = stockstream.api.get_votes_by_date(datestr)
    for vote in votes:
        players.add(vote['username'])
    start = start + timedelta(days=1)

print "{} total users.".format(len(players))

calculateParallel(players)


#scheduler.update_profile("twitch:funkmasterflexion")
