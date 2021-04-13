from structs import GameConfiguration
from bulk_tournament import bulk_tournament
from players import *


def roundrobin(players: List[PlayerAlgorithm] = PlayerAlgorithm.all(), silent: bool = False,
               seed: int = None, config: GameConfiguration = GameConfiguration()) -> dict:
    """
    Play each player against each other player once, and return a dictionary where keys are players and values are a
    list of players that player beat.

    This is just a specialized form of bulk_tournament, with some output reformatting.
    """
    if not seed:
        seed = random_seed()

    if not silent:
        print(f"Playing a Nannon{config} round robin between {', '.join(player.name for player in players)}. seed = {seed}")

    advantages = bulk_tournament(players, rounds=1, silent=True, seed=seed, config=config)

    scores = {winner: [loser for loser in advantages[winner] if advantages[winner][loser] > 0] for winner in advantages}

    if not silent:
        print("Results:")
        for winner in scores:
            print(f"{winner.name} beat: {', '.join(loser.name for loser in scores[winner])}")

    return scores
