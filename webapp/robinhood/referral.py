import os


def get_referral():
    return os.environ.get("ROBINHOOD_REFERRAL")
