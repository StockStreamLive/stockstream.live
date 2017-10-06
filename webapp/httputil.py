import requests
import traceback
from expiringdict import ExpiringDict
import os


max_cache_items = os.environ['CACHE_SIZE']
max_cache_age = os.environ['CACHE_AGE']

url_cache = ExpiringDict(max_len=max_cache_items, max_age_seconds=max_cache_age)


def get_json_object_from_url(url):
    if url in url_cache:
        return url_cache[url]

    print "Retrieving url: " + url

    try:
        returned_object = requests.get(url)
        returned_object = returned_object.json()

    except Exception as ex:
        print "Warning: " + `ex` + " from url " + url
        traceback.print_exc()
        return None

    url_cache[url] = returned_object

    return returned_object
