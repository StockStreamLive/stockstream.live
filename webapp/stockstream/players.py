import stockstream


def get_top_players_list():
    player_profiles = []

    top_players = stockstream.api.get_ranked_players()[:6]

    for player in top_players:
        positions = stockstream.api.get_positions_by_player(player)
        player_profile = stockstream.positions.assemble_positions(positions)

        profile_stats = player_profile['profile_statistics']

        total_trades = float(profile_stats['profitable_trades'] + profile_stats['unprofitable_trades'])
        total_trades = 1 if total_trades == 0 else total_trades
        percent_profitable = (profile_stats['profitable_trades'] / total_trades) * 100

        player_profile['profile_statistics']['percent_profitable'] = percent_profitable
        player_profile['username'] = player

        player_profiles.append(player_profile)

    return player_profiles
