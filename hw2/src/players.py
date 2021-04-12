from typing import *
from random import choice

from helpers import *
from main import Move, Player

class PlayerAlgorithm:
    @classmethod
    def all(cls):
        return all_subclasses(cls)

    @classmethod
    def get(cls, name: str, *args, **kwargs) -> 'PlayerAlgorithm':
        AlgClass = only((c for c in cls.all() if c.name == name), "couldn't find PlayerAlgorithm!")
        return AlgClass(*args, **kwargs)

    @property
    def name(self) -> str:
        """
        Return the human-readable name of this play algorithm.
        """
        raise NotImplementedError("Do not use PlayerAlgorithm directly!")

    def play(self, moves: List[Move], roll: int) -> Move:
        """
        Pick which move to play.
        """
        raise NotImplementedError("Do not use PlayerAlgorithm directly!")

    @property
    def force_silent(self) -> bool:
        """
        If true, forcibly prevents any printing of this algorithm's moves. Used by HumanPlayerAlgorithm to avoid telling
        the user that they made the move they just chose to make.
        """
        return False


class HumanPlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that prompts the user to select a move.
    """
    name = "human"
    force_silent = True

    def play(self, moves: List[Move], roll: int) -> Move:
        print(f"Your Turn (You Rolled {roll}):")
        print(join_horizontal((move.draw(Player.BLACK) for move in moves), '\t'))

        selection = int(input(f"Select an Option (1-{len(moves)}):"))
        if not (1 <= selection <= len(moves)):
            print("Invalid Selection!")
            return self.play(moves, roll)

        return moves[selection - 1]


class RandomPlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that picks a move at random.
    """
    name = "random"

    def play(self, moves: List[Move], roll: int) -> Move:
        return choice(moves)

