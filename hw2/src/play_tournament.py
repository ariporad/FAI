from main import GameConfiguration
from Dicestream import Dicestream
from play_game import play_game
from players import *


def play_tournament(player1: PlayerAlgorithm, player2: PlayerAlgorithm, n_pairs: int = 100, dicestream: Dicestream = None, seed: int = None, config: GameConfiguration = GameConfiguration(), silent: bool = False) -> float:
    """
    Play player1 against player2 `2 * n_pairs` times, and return the proportion of the time that player1 wins.
    """
    if dicestream is None:
        if seed is None:
            seed = random_seed()

        dicestream = Dicestream.random(config.die_size, seed)
    else:
        assert seed is None, "can't provide a seed and a dicestream"

    n = 2 * n_pairs

    progress = None
    if not silent:
        print(f"Playing a Nannon{config} tournament of {n} games, {player1.name} vs {player2.name}. seed = {seed}")
        progress = ProgressBar(time=True)

    wins = 0
    for i in range(0, n):
        if not silent:
            progress.update(i / n, f"Playing Game {i + 1}/{n} ({round(100 * wins / (i + 1), 1)}% won by {player1.name})...")
        winner = play_game(player1, player2, dicestream, config=config, silent=True)
        if winner == Player.BLACK:
            wins += 1

    if not silent:
        progress.stop(f"Played {n} games {player1.name} vs {player2.name}: {player1.name} won {wins} ({round(100 * wins / n, 2)}%).")
    
    return wins / n
    
    
if __name__ == '__main__':
    play_tournament(RandomPlayerAlgorithm(), RandomPlayerAlgorithm())
