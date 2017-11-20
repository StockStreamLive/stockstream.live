from twitch import TwitchClient

channel_cache = {}


def get_channel_for_user(username):
    if username in channel_cache:
        return channel_cache[username]

    client = TwitchClient(client_id='ohlre6lyirmibqf5jhxz8taxnnc3m6')
    users = client.users.translate_usernames_to_ids([username])

    if len(users) <= 0:
        channel = {
            'display_name': username,
            'logo': "/static/8bitmoney.png"
        }
    else:
        channel = client.channels.get_by_id(users[0]['id'])

    if channel['logo'] is None:
        channel['logo'] = "/static/8bitmoney.png"

    channel_cache[username] = channel

    return channel
