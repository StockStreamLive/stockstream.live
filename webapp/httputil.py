import requests
import traceback
from expiringdict import ExpiringDict

url_cache = ExpiringDict(max_len=7500, max_age_seconds=150)


def get_json_object_from_url(url):
    if url in url_cache:
        return url_cache[url]

    try:
        object = requests.get(url).json()
    except Exception as ex:
        print "Warning: " + `ex`
        traceback.print_exc()
        return None

    print "{} items in the url cache".format(len(url_cache))

    url_cache[url] = object

    return object
