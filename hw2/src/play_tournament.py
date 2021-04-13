from structs import GameConfiguration
from Dicestream import Dicestream
from play_game import play_game
from players import *


def play_tournament(player1: PlayerAlgorithm, player2: PlayerAlgorithm, rounds: int = 100, dicestream: Dicestream = None, seed: int = None, config: GameConfiguration = GameConfiguration(), silent: bool = False) -> float:
    """
    Play player1 against player2 `rounds` times, and return the proportion of the time that player1 wins.
    """
    if dicestream is None:
        if seed is None:
            seed = random_seed()

        dicestream = Dicestream.random(config.die_size, seed)
    else:
        assert seed is None, "can't provide a seed and a dicestream"

    progress = None
    if not silent:
        print(f"Playing a Nannon{config} tournament of {rounds} games, {player1.name} vs {player2.name}. seed = {seed}")
        progress = ProgressBar(time=True)

    wins = 0
    for i in range(0, rounds):
        if not silent:
            progress.update(i / rounds, f"Playing Game {i + 1}/{rounds} ({round(100 * wins / (i + 1), 1)}% won by {player1.name})...")
        winner = play_game(player1, player2, dicestream, config=config, silent=True)
        if winner == Player.BLACK:
            wins += 1

    if not silent:
        progress.stop(f"Played {rounds} games {player1.name} vs {player2.name}: {player1.name} won {wins} ({round(100 * wins / rounds, 2)}%).")
    
    return wins / rounds
    
    
if __name__ == '__main__':
    play_tournament(RandomPlayerAlgorithm(), RandomPlayerAlgorithm())
