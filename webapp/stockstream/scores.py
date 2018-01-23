import stockstream
import twitch_api


def get_ranked_scores():
    ranked_scores = stockstream.api.get_ranked_scores()
    return augment_ranked_scores(ranked_scores)


def augment_ranked_scores(ranked_scores):
    scores_to_display = [score for score in ranked_scores if score['qualifiedTrades'] > 0]
    ranked_scores = scores_to_display

    players = [score['playerId'].split(":")[1] for score in ranked_scores]
    channels = twitch_api.get_channels_for_users(players)

    player_to_score = {}
    for score in ranked_scores:
        player = score['playerId'].split(":")[1]
        player_to_score[player] = score

    for channel in channels:
        login = channel['name']
        score = player_to_score[login]
        score['channel'] = channel
        player_to_score[login] = score

    return ranked_scores
