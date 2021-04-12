from typing import *
from random import choice

from helpers import *
from main import Move, Player


def human_player(moves: List[Move], roll: int) -> Move:
    """
    A Nannon player that prompts the user to select a move.
    """
    
    print(f"Your Turn (You Rolled {roll}):")
    print(join_horizontal((move.draw(Player.BLACK) for move in moves), '\t'))
    
    choice = int(input(f"Select an Option (1-{len(moves)}):"))
    if not (1 <= choice <= len(moves)):
        print("Invalid Selection!")
        return human_player(moves, roll)
    
    return moves[choice - 1]


def random_player(moves: List[Move], roll: int) -> Move:
    """
    A Nannon player that picks a move at random.
    """
    return choice(moves)


def make_player_verbose(player, name: str = "Player"):
    """
    Wrap a player to make it print every move it makes.
    """
    
    def new_player(moves: List[Move], roll: int) -> Move:
        print(f"{name} (Rolled {roll}) Picked:")
        move = player(moves, roll)
        print(move.draw(Player.BLACK))
        return move
    
    new_player.__name__ = player.__name__
    
    return new_player

verbose_random_player = make_player_verbose(random_player, 'Random Player')

PLAYERS = {
    'random': random_player,
    'human': human_player,
}