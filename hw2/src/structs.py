"""
This file contains various data containers (structs in other languages, hence the name), which contain no real logic.
"""
from enum import Enum
from dataclasses import dataclass
from functools import total_ordering, cached_property, cache
from typing import *


class Player(Enum):
    """
    An enum representing both options for players (Black and White).
    """
    BLACK = 'BLACK'
    WHITE = 'WHITE'

    @property
    def swapped(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE

    @property
    def short_str(self) -> str:
        """
        A very short (ie. one letter) symbol identifying the player, mostly used for debugging.
        """
        return "B" if self == Player.BLACK else "W"

    @property
    def long_str(self) -> str:
        """
        Human-readable name of this player.
        """
        return "Black" if self == Player.BLACK else "White"

    @cached_property
    def int_value(self):
        return 1 if self == Player.BLACK else 2

    @cached_property
    def display_symbol(self) -> str:
        return '○' if self == Player.WHITE else '●'

    def __repr__(self):
        return "Player.BLACK" if self == Player.BLACK else "Player.WHITE"


class GameConfiguration(NamedTuple):
    """
    A named tuple representing the particular variant of Nannon we're playing. Completely immutable.

    The defaults represent standard Nannon, with a 6 positions on the board, 3 checkers per player,
    and a standard six-sided die.
    """

    board_size: int = 6
    checkers_per_player: int = 3
    die_size: int = 6

    # def __new__(cls, board_size, checkers_per_player, die_size):
    #     assert checkers_per_player < die_size, "checkers per player must be less than die size to avoid stalemates"
    #     return super(cls, GameConfiguration).__new__(GameConfiguration, (board_size, checkers_per_player, die_size))

    def __str__(self):
        return f"{{{self.board_size},{self.checkers_per_player},{self.die_size}}}"



@dataclass
@total_ordering
class Checker:
    """
    An immutable data class representing a Checker.
    """

    class Position(int):
        """
        A wrapper around int representing a checker's position. Can support either numerical positions (which are always
        non-negative integers, where 0 is the position closest to the perspective player's home), or abstract positions,
        like 'HOME' (Checker.Position.HOME_VALUE), or 'GOAL' (Checker.Position.GOAL_VALUE).

        Access abstract positions like an enum:
        >>> print(Checker.Position('HOME'))
        Checker.Position(HOME)
        >>> print(Checker.Position('GOAL'))
        Checker.Position(GOAL)

        Access concrete positions like a constructor:
        >>> print(Checker.Position(4))
        Checker.Position(4)

        Checker.Positions are immutable value types:
        >>> Checker.Position(4) == Checker.Position(4)
        True
        >>> Checker.Position(4) == Checker.Position(5)
        False
        >>> Checker.Position('HOME') == Checker.Position('HOME')
        True
        >>> Checker.Position('GOAL') == Checker.Position('GOAL')
        True
        >>> Checker.Position('HOME') == Checker.Position('GOAL')
        False
        >>> Checker.Position('GOAL') == Checker.Position('HOME')
        False

        Concrete Checker.Positions are ints, so they can be used as such:
        >>> ['Zero', 'One', 'Two', 'Three'][Checker.Position(2)]
        'Two'
        >>> Checker.Position('HOME')
        -1
        """

        HOME_VALUE = -1
        GOAL_VALUE = 100  # this just needs to be bigger than any other position

        Value = Union[int, Literal['HOME', 'GOAL'], 'Checker.Position']

        def __new__(cls, value: Value):
            if isinstance(value, str):
                if value == 'HOME':
                    value = cls.HOME_VALUE
                elif value == 'GOAL':
                    value = cls.GOAL_VALUE
                else:
                    raise TypeError('Valid string values for Checker.Position are "HOME" and "GOAL".')
            return int.__new__(cls, value)

        def __str__(self):
            return f"Checker.Position({self.name})"

        @property
        def is_concrete(self) -> bool:
            return self != Checker.Position.HOME_VALUE and self != Checker.Position.GOAL_VALUE

        def swap(self, board_size: int) -> 'Checker.Position':
            return Checker.Position(board_size - 1 - self)

        @property
        def name(self) -> str:
            if self == Checker.Position('GOAL'):
                return "GOAL"
            elif self == Checker.Position('HOME'):
                return "HOME"
            else:
                return int.__str__(self)

    player: Player
    position: Position

    def __post_init__(self):
        if not isinstance(self.position, Checker.Position):
            self.position = Checker.Position(self.position)

    def __str__(self):
        return f"Checker({self.player.short_str} @ {self.position.name})"

    def __eq__(self, other: 'Checker'):
        return self.hash_value == other.hash_value

    # Because of aggressive caching, caching the hash value itself provides a significant performance boost
    def __hash__(self):
        return self.hash_value

    @cached_property
    def hash_value(self):
        return (self.position << 2) + self.player.int_value

    def __lt__(self, other: 'Checker'):
        if self.position != other.position:
            return self.position < other.position
        else:
            return self.player == Player.BLACK
