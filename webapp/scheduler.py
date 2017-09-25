import stockstream
import s3util
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler

last_update = 0


def update_profile(username):
    print "Updating {}".format(username)
    profile = stockstream.positions.assemble_positions(username)
    path = username.replace(":", "/")
    s3util.write_file_data("api.stockstream.live", "profile/" + path, json.dumps(profile))


def update_profiles():
    global last_update
    votes = stockstream.api.get_votes_today()
    modded_voters = set([vote['username'] for vote in votes if 'orderId' in vote and vote['timestamp'] > last_update])
    print "Updating users {} since they were modded after last update of {}".format(modded_voters, last_update)
    for username in modded_voters:
        update_profile(username)
    last_update = int(round(time.time() * 1000))


def schedule_jobs():
    scheduler = BlockingScheduler()
    scheduler.add_job(update_profiles, 'interval', minutes=5)
    scheduler.start()

if __name__ == "__main__":
    ctime = time.time()
    update_profiles()
    ntime = time.time()
    print ntime - ctime