from dataclasses import dataclass
from functools import total_ordering
from math import inf
from typing import *

from Player import Player


@dataclass(frozen=True)
class Checker:
    """
    An immutable data class representing a Checker.
    """

    @total_ordering
    class Position:
        """
        A pseudo-enum representing a checker's position. Can support either numerical positions (which
        are always non-negative integers, where 0 is the position closest to the checker's home), or
        abstract positions, like 'HOME', or 'GOAL'.

        Access abstract positions like an enum:
        >>> print(Checker.Position.HOME)
        Checker.Position(HOME)
        >>> print(Checker.Position.GOAL)
        Checker.Position(GOAL)

        Access concrete positions like a constructor:
        >>> print(Checker.Position(4))
        Checker.Position(4)

        Checker.Positions are immutable value types:
        >>> Checker.Position(4) == Checker.Position(4)
        True
        >>> Checker.Position(4) == Checker.Position(5)
        False
        >>> Checker.Position.HOME == Checker.Position.HOME
        True
        >>> Checker.Position.GOAL == Checker.Position.GOAL
        True
        >>> Checker.Position.HOME == Checker.Position.GOAL
        False
        >>> Checker.Position.GOAL == Checker.Position.HOME
        False

        Concrete Checker.Positions' values can be accessed with .index, or can be casted to/from ints:
        >>> Checker.Position(4).index
        4
        >>> ['Zero', 'One', 'Two', 'Three'][Checker.Position(2)]
        'Two'

        Abstract Checker.Positions will raise an exception if you try to do this:
        >>> Checker.Position.HOME.index
        Traceback (most recent call last):
            ...
        AssertionError: Can't get the index of abstract Checker.Position! You should check for this!
        >>> ['Zero', 'One', 'Two', 'Three'][Checker.Position.HOME]
        Traceback (most recent call last):
            ...
        AssertionError: Can't get the index of abstract Checker.Position! You should check for this!
        """

        # These will be initialized later, they're just here for typing
        HOME = None  # type: 'Position'
        GOAL = None  # type: 'Position'

        def __init__(self, value: int, abstract_label: Optional[str] = None):
            self.is_concrete = not abstract_label
            self._value = value
            self._label = abstract_label

        def __str__(self):
            return f"Checker.Position({self.debug_str})"

        def __eq__(self, other: 'Checker.Position'):
            return isinstance(other, self.__class__) and other.is_concrete == self.is_concrete and (
                other._value == self._value if self.is_concrete else other._label == self._label)

        def __gt__(self, other: 'Checker.Position'):
            return int(self) > int(other)

        def __int__(self):
            return self._value

        def __index__(self):
            return self.index
        
        @property
        def debug_str(self) -> str:
            return str(self._label or self._value)

        @property
        def index(self) -> int:
            assert self.is_concrete, "Can't get the index of abstract Checker.Position! You should check for this!"
            return self._value
        

    player: Player
    position: Position

    def __str__(self):
        return f"Checker({self.player.short_str} @ {self.position.debug_str})"
    
    @property
    def display_symbol(self) -> str:
        return '○' if self.player == Player.BLACK else '●'
    


Checker.Position.HOME = Checker.Position(-inf, abstract_label='HOME')
Checker.Position.GOAL = Checker.Position(+inf, abstract_label='GOAL')
