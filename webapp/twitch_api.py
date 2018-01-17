from twitch import TwitchClient

twitch_client_id = 'ohlre6lyirmibqf5jhxz8taxnnc3m6'

channel_cache = {}


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_channel_for_user(username):
    if username in channel_cache:
        return channel_cache[username]

    client = TwitchClient(client_id=twitch_client_id)
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


def get_channels_for_users(usernames):
    client = TwitchClient(client_id=twitch_client_id)

    all_channels = []

    batches = chunks(usernames, 50)
    for batch in batches:
        channels = client.users.translate_usernames_to_ids(batch)
        all_channels.extend(channels)

    return all_channels

