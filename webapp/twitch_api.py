from twitch import TwitchClient

channel_cache = {}


def get_channel_for_user(username):
    if username in channel_cache:
        return channel_cache[username]

    client = TwitchClient(client_id='ohlre6lyirmibqf5jhxz8taxnnc3m6')
    users = client.users.translate_usernames_to_ids([username])
    channel = client.channels.get_by_id(users[0]['id'])

    channel_cache[username] = channel

    return channel
