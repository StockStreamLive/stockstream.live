import requests
import traceback
from expiringdict import ExpiringDict

url_cache = ExpiringDict(max_len=200, max_age_seconds=150)


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

    url_cache[url] = returned_object

    return returned_object
