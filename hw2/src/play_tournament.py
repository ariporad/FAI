from main import GameConfiguration
from Dicestream import Dicestream
from play_game import play_game
from players import *


def play_tournament(player1, player2, n_pairs: int = 100, dicestream: Dicestream = Dicestream.random(), config: GameConfiguration = GameConfiguration()) -> float:
    """
    Play player1 against player2 `2 * n_pairs` times, and return the proportion of the time that player1 wins.
    """
    n = 2 * n_pairs
    
    wins = 0
    progress = ProgressBar(time=True)
    for i in range(0, n):
        progress.update(i / n, f"Playing Game {i + 1}/{n} ({round(100 * wins / (i + 1), 1)}% won by {player1.__name__})...")
        winner = play_game(player1, player2, dicestream, config=config, silent=True)
        if winner == Player.BLACK:
            wins += 1
    
    progress.stop(f"Played {n} games {player1.__name__} vs {player2.__name__}: {player1.__name__} won {wins} ({round(100 * wins / n, 2)}%).")
    
    return wins / n
    
    
if __name__ == '__main__':
    play_tournament(random_player, random_player)
