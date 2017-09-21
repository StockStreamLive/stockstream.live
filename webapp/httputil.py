import requests
import traceback
from expiringdict import ExpiringDict
import sys

url_cache = ExpiringDict(max_len=500, max_age_seconds=150)


def get_json_object_from_url(url):
    if url in url_cache:
        return url_cache[url]

    try:
        returned_object = requests.get(url)
        returned_object = returned_object.json()

    except Exception as ex:
        print "Warning: " + `ex` + " from url " + url
        traceback.print_exc()
        return None

    print "{} items in the url cache".format(len(url_cache))

    url_cache[url] = returned_object

    return returned_object
