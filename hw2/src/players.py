from typing import *
from random import choice

from helpers import *
from main import Move, Player


class PlayerAlgorithm:
    """
    An abstract class representing one algorithm for playing Nannon.
    """

    @classmethod
    def all(cls):
        """
        Return all available Nannon PlayerAlgorithms.

        Uses the magic of Python to detect all PlayerAlgorithm subclasses that have been defined without any other
        tracking.
        """
        return all_subclasses(cls)

    @classmethod
    def get(cls, name: str, *args, **kwargs) -> 'PlayerAlgorithm':
        """
        Get an instance of the PlayerAlgorithm called "name".

        NOTE: This returns an instance, not the class.
        NOTE: name refers to the instance's .name property.

        Uses the magic of Python to detect all PlayerAlgorithm subclasses that have been defined without any other
        tracking.
        """
        AlgClass = only((c for c in cls.all() if c.name == name), "couldn't find PlayerAlgorithm!")
        return AlgClass(*args, **kwargs)

    def play(self, moves: List[Move], roll: int) -> Move:
        """
        Pick which move to play.

        For a shortcut to implementing this for many use cases, see rank().
        """
        return sorted(moves, key=lambda m: self.rank(m), reverse=True)[0]

    def rank(self, move: Move) -> int:
        """
        Many algorithms simply calculate a numerical value for each move and pick the move with the highest (or lowest)
        value. For those, they can simply implement rank(move), and PlayerAlgorithm will provide a play implementation.

        For the default implementation, PlayerAlgorithm will pick the move with the value closest to positive infinity.
        If an implementation wants to instead pick the lowest value, simply multiply the values by -1.
        """
        raise NotImplementedError("Abstract method: do not use PlayerAlgorithm directly!")

    @property
    def name(self) -> str:
        """
        Return the human-readable name of this play algorithm.
        """
        raise NotImplementedError("Abstract method: do not use PlayerAlgorithm directly!")

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

        try:
            selection = int(input(f"Select an Option (1-{len(moves)}): "))
            if not (1 <= selection <= len(moves)):
                raise ValueError()
        except ValueError:
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


class FirstPlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that always moves the furthest-forward checker in the hope of getting as many as possible off the
    board.
    """
    name = "first"

    def rank(self, move: Move) -> int:
        return move.checker.position


class LastPlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that always moves the checker closest to home in the hope of getting as many as possible on the
    board.
    """
    name = "last"

    def rank(self, move: Move) -> int:
        return -move.checker.position


class ScorePlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that tries to maximize the difference between a player's scores.
    """
    name = "score"

    def rank(self, move: Move) -> int:
        player = move.player
        return move.executed.score(player) - move.executed.score(player.swapped)

