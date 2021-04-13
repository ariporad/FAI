from typing import *
from random import choice

from helpers import *
from structs import *
from Board import Board, Move


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
        # We sort here to ensure consistency, which makes some other things simpler
        return sorted(all_subclasses(cls), key=lambda c: c.name)

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
        return sorted(moves, key=lambda m: self.rank(m, roll), reverse=True)[0]

    def rank(self, move: Move, roll: int) -> float:
        """
        Many algorithms simply calculate a numerical value for each move and pick the move with the highest (or lowest)
        value. For those, they can simply implement rank(move), and PlayerAlgorithm will provide a play implementation.

        For the default implementation, PlayerAlgorithm will pick the move with the value closest to positive infinity.
        If an implementation wants to instead pick the lowest value, simply multiply the values by -1.
        """
        raise NotImplementedError("Abstract method: do not use PlayerAlgorithm directly!")

    # These getters can be overwritten with normal properties
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

    def rank(self, move: Move, roll: int) -> float:
        # Always pick the move with the checker with the greatest (closest to goal) position.
        return move.checker.position


class LastPlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that always moves the checker closest to home in the hope of getting as many as possible on the
    board.
    """
    name = "last"

    def rank(self, move: Move, roll: int) -> float:
        # Always pick the move with the lowest (closest to home) position.
        return -move.checker.position


class ScorePlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player that tries to maximize the difference between a player's scores.
    """
    name = "score"

    def rank(self, move: Move, roll: int) -> float:
        player = move.player
        return self.score(move.executed, player) - self.score(move.executed, player.swapped)

    def score(self, board: Board, player: Player):
        """
        Return player's score, which is the sum of the position of all the checkers (where home is 0pts, the board is
        1...board_size pts, and the goal is board_size + 1 pts).
        """
        board = board.from_perspective(player)

        total = 0
        for checker in board.checkers:
            if checker.player != player:
                continue

            if checker.position == Checker.Position('HOME'):
                # Home is 0 points
                continue
            elif checker.position == Checker.Position('GOAL'):
                total += board.config.board_size + 1
            else:
                total += checker.position + 1

        return total


class KnowledgePlayerAlgorithm(PlayerAlgorithm):
    """
    A Nannon player based on my intuition. It does a minimax of its score and the opponent's score, with additional
    consideration about the move itself. Its guiding principles are:
    - Checkers closer to the goal are better. (Similarly to, but weighted differently than, ScorePlayerAlgorithm)
    - Knocking off an opponent's checker is valuable, proportionally to how close it is to its goal
    - Using a roll of 6 to move a checker that's 1 away from the goal is a waste

    Those principles are combined with weights derived from experimentation to build the algorithm.
    """
    name = "knowledge"

    def rank(self, move: Move, roll: int) -> float:
        """
        Return the overall score of the move, which is composed of both the move score and board score.
        """
        own_board_score = self.board_score(move.executed, move.player)
        other_board_score = self.board_score(move.executed, move.player.swapped)
        move_score = self.move_score(roll, move)

        return (own_board_score - other_board_score) + move_score

    def move_score(self, roll: int, move: Move) -> float:
        """
        Return the score of the move itself, which takes into account captures and fully using the dice roll. This is
        only part of the move's overall score.
        """
        total = 0

        if move.captured is not None:
            total += 1.5 * self.position_score(
                move.captured.position.swap(move.board.config.board_size),
                move.board.config.board_size
            )

        if move.to == Checker.Position('GOAL'):
            spots_moved = move.board.config.board_size - move.checker.position
            total += 3 * (spots_moved - roll)

        return total

    def position_score(self, position: Checker.Position, board_size: int):
        """
        Return the score of a checker at position.

        WARNING: Make sure the position is from the right perspective before calling this method.
        """
        # We can't just use the board position like ScorePlayerAlgorithm, because we need to be able to weight it for
        # all possible board sizes. Therefore, we scale it from 0-10, with the goal as 11.
        if position == Checker.Position('GOAL'):
            return 11
        return (10 / board_size) * float(position)

    def board_score(self, board: Board, player: Player) -> float:
        """
        Return board score, which is the sum of all the checker position scores. This is only part of a move's overall
        score.
        """
        board = board.from_perspective(player)

        return sum(self.position_score(checker.position, board.config.board_size) for checker in board.checkers if checker.player == player)

