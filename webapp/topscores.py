import json
import os
import stockstream

files = os.listdir("twitch")

t_total = 0


for f in files:
    profile = json.loads(open("twitch/"+f).read())
    stats = stockstream.player.get_profile_statistics(profile)
    total = stats['realized_return'] + stats['unrealized_return']
    t_total += total
    print "{} {} {} {}".format(f, total, stats['realized_return'], stats['unrealized_return'])

print "Total: " + `t_total`

"""for f in files:
    if not f.startswith("twitch:"):
        continue
    newname = f.split(":")[1]
    print "Renaming " + "twitch/" + f + " to " + "twitch/" + newname
    os.rename("twitch/" + f, "twitch/" + newname)
"""