

def compute_order_id_to_votes(votes):
    id_to_votes = {}
    for vote in votes:
        if 'order_id' not in vote or vote['order_id'] is None:
            continue
        order_id = vote['order_id']
        if order_id not in id_to_votes:
            id_to_votes[order_id] = []
        id_to_votes[order_id].append(vote)
    return id_to_votes
