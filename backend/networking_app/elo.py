# Straight from Chat. please update as needed


def update_elo_batch(players: list[dict[str, float]], matches: list[tuple[str, str, str]], K=32):
    """
    STRAIGHT FROM GPT
    Update ratings for one 'batch' (simultaneous) round of matches.

    :param players: dict {player_name: current_rating}
    :param matches: list of tuples (player1, player2, winner)
                    e.g. ("Alice", "Bob", "Alice") means Alice beat Bob
    :param K:       Elo K-factor
    """

    # Initialize expected/actual scores for each player
    expected_scores = {p: 0.0 for p in players}
    actual_scores = {p: 0.0 for p in players}

    # --- 1) Calculate expected and actual scores ---
    for p1, p2, winner in matches:
        r1 = players[p1]
        r2 = players[p2]

        # Expected score for p1 (standard Elo formula)
        E1 = 1.0 / (1 + 10 ** ((r2 - r1) / 400.0))
        E2 = 1.0 - E1  # for p2

        expected_scores[p1] += E1
        expected_scores[p2] += E2

        # Actual score: 1 for winner, 0 for loser
        if winner == p1:
            actual_scores[p1] += 1.0
        elif winner == p2:
            actual_scores[p2] += 1.0
        else:
            continue

    # --- 2) Update ratings in one shot ---
    new_ratings = {}
    for p in players:
        old_rating = players[p]
        # difference = (actual - expected)
        diff = actual_scores[p] - expected_scores[p]
        new_ratings[p] = old_rating + K * diff

    # Apply the updates simultaneously
    for p in players:
        players[p] = new_ratings[p]


# ----------------------------
# Example usage:
if __name__ == "__main__":
    # 1) Initial ratings
    players = {"Alice": 1500, "Bob": 1500, "Charlie": 1500, "David": 1500}

    # 2) Matches in one 'simultaneous' round:
    #    (p1, p2, winner)
    matches = [
        ("Alice", "Bob", "Alice"),  # Alice beats Bob
        ("Charlie", "David", "David"),
        ("Bob", "Charlie", "Bob"),
        ("Alice", "David", "David"),
        ("Alice", "David", "David"),
        ("Alice", "David", "David"),
        ("Alice", "David", "David"),
        ("Bob", "David", "Bob"),
    ]

    # 3) Single-round Elo update
    update_elo_batch(players, matches, K=32)

    # 4) Check updated ratings
    for name, rating in players.items():
        print(f"{name}: {rating:.2f}")
