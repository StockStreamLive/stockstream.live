import requests
import traceback


def get_json_object_from_url(url):
    print("Retrieving url: " + url)

    try:
        returned_object = requests.get(url)
        returned_object = returned_object.json()

    except Exception as ex:
        print("Warning: " + str(ex) + " from url " + url)
        traceback.print_exc()
        return None

    return returned_object


def post_object_to_url(url, obj):
    print("Retrieving url: " + url)

    try:
        returned_object = requests.post(url, obj)
        returned_object = returned_object.json()

    except Exception as ex:
        print("Warning: " + str(ex) + " from url " + url)
        traceback.print_exc()
        return None

    return returned_object
