from random import Random
from typing import *


class Dicestream(Iterator[int]):
    """
    An iterator representing a stream of dice rolls. Each roll is an integer between 1 and die_size,
    inclusive.

    This is just a wrapper around another Iterator to enable specifying a die_size.
    """
    
    die_size: int
    _iterator: Iterator[int]
    
    def __init__(self, iterable: Iterable[int], die_size: int = 6):
        self.die_size = die_size
        self._iterator = iter(iterable)
    
    def __next__(self) -> int:
        return next(self._iterator)
    
    def roll(self) -> int:
        """
        Return the next roll of the dice.
        """
        return next(self)
    
    def first_roll(self) -> int:
        """
        Calculate the first roll of the game, as follows: two dice are rolled, and the difference is returned. In the
        event of a tie, re-roll the dice. This may result in either a positive or negative number, which should be
        interpreted as in favor of one player or another. Which player is which doesn't matter, by definition.
        
        NOTE: This method just performs the computation. It does not enforce that it is actually the game's first roll.

        >>> Dicestream.fixed([1, 5]).first_roll()
        -4
        >>> Dicestream.fixed([2, 2, 3, 3, 4, 2]).first_roll()
        2
        """
        diff = self.roll() - self.roll()
        
        if diff == 0:
            return self.first_roll()
        
        return diff
    
    @classmethod
    def random(cls, die_size: int = 6, seed: int = None) -> 'Dicestream':
        """
        Return a dicestream that produces uniformly random rolls.
        
        >>> dicestream = Dicestream.random(die_size = 6, seed = 1) # deterministic because seed is specified
        >>> next(dicestream)
        2
        >>> next(dicestream)
        5
        >>> dicestream.roll()
        1
        >>> dicestream.roll()
        3
        """
        
        def random_iterator():
            random = Random(seed)
            
            while True:
                yield random.randint(1, die_size)
        
        return cls(random_iterator(), die_size)
    
    @classmethod
    def fixed(cls, rolls: List[int], die_size: int = 6) -> 'Dicestream':
        """
        Return a dicestream that produces the rolls perscribed, in order.

        >>> dicestream = Dicestream.fixed([1, 2, 3, 4])
        >>> next(dicestream)
        1
        >>> next(dicestream)
        2
        >>> next(dicestream)
        3
        >>> next(dicestream)
        4
        """
        assert all([1 <= item and item <= die_size for item in rolls]), "all rolls must be in range [1, die_size]"
        
        return cls(rolls, die_size)
