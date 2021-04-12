from main import GameConfiguration
from Dicestream import Dicestream
from play_tournament import play_tournament
from players import *


def bulk_tournament(players: List[PlayerAlgorithm] = PlayerAlgorithm.all(), n_pairs: int = 100, silent: bool = False,
               seed: int = None, config: GameConfiguration = GameConfiguration()) -> dict:
    """
    Play player1 against player2 `2 * n_pairs` times, and return the proportion of the time that player1 wins.
    """
    if not seed:
        seed = random_seed()

    dicestream = Dicestream.random(config.die_size, seed)

    n = 2 * n_pairs

    progress = None

    if not silent:
        print(f"Playing a Nannon{config} bulk tournament of {n} games each between {', '.join(player.name for player in players)}. seed = {seed}")
        progress = ProgressBar(time=True)

    num_players = len(players)
    pairings = [(players[i], players[j]) for i in range(0, num_players) for j in range(i + 1, num_players)]
    num_pairings = len(pairings)

    # advantages[A][B] is the proportion of the time that A beat B
    advantages = {player: {} for player in players}

    for i in range(0, num_pairings):
        black_player, white_player = pairings[i]
        progress.update(i / num_pairings, f"Playing Tournament {i + 1}/{num_pairings}: {black_player.name} vs {white_player.name}...")
        advantage = play_tournament(black_player, white_player, n_pairs, dicestream=dicestream, config=config, silent=True)
        advantages[black_player][white_player] = advantage
        advantages[white_player][black_player] = 1 - advantage

    col_order = sorted(players, key=lambda p: p.name)
    maxlen = max([len('Loser →')] + [len(player.name) for player in col_order])

    progress.stop(f"Played {num_pairings} tournaments of {n_pairs * 2} games each.")

    format_row = lambda items: ' | '.join(str(n).ljust(maxlen) for n in items)

    title_row = format_row(['Loser →'] + [player.name for player in col_order])

    if not silent:
        print(title_row)
        print('-' * len(title_row))
        for row_player in advantages.keys():
            values = [(f"{round(advantages[row_player][col_player] * 100, 1)}%" if row_player != col_player else '-') for col_player in col_order]
            print(format_row([row_player.name] + values))

    return advantages


if __name__ == '__main__':
    play_tournament(RandomPlayerAlgorithm(), RandomPlayerAlgorithm())
