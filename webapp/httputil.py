import requests
import traceback
from expiringdict import ExpiringDict
import os





def get_json_object_from_url(url):
    # if url in url_cache:
    #    return url_cache[url]

    print "Retrieving url: " + url

    try:
        returned_object = requests.get(url)
        returned_object = returned_object.json()

    except Exception as ex:
        print "Warning: " + `ex` + " from url " + url
        traceback.print_exc()
        return None

    # url_cache[url] = returned_object

    return returned_object
