import requests
import traceback
import cached


@cached.cached()
def get_json_object_from_url(url):
    print "Retrieving url: " + url

    try:
        returned_object = requests.get(url)
        returned_object = returned_object.json()

    except Exception as ex:
        print "Warning: " + `ex` + " from url " + url
        traceback.print_exc()
        return None

    return returned_object
