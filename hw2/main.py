#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Optional
from random import Random

@dataclass
class Game:
	board_size: int = 6
	checkers_per_player: int = 3
	die_size: int = 6
	seed: Optional[int] = None
	random: Random = field(init=False)

	def __post_init__(self):
		# Sanity Check
		assert self.checkers_per_player < self.die_size, "checkers per player must be less than die size to avoid stalemates"

		self.random = Random(self.seed)

	def roll(self):
		"""
		Return a uniformly random integer between 1 and die_size, inclusive.
		
		>>> game = Game(seed = 1) # deterministic because seed is specified
		>>> game.roll()
		2
		>>> game.roll()
		5
		>>> game.roll()
		1
		>>> game.roll()
		3
		"""
		return self.random.randint(1, self.die_size)

	def first_roll(self):
		"""
		Calculate the first roll of the game, as follows: two dice are rolled, and the difference is
		returned. In the event of a tie, re-roll the dice.
		"""
		diff = abs(self.roll() - self.roll())

		if diff == 0:
			return self.first_roll()

		return diff








### Configuration Parameters ###
BOARD_SIZE = 6
CHECKERS_PER_PLAYER = 3
DIE_SIZE = 6

assert CHECKERS_PER_PLAYER < DIE_SIZE # Required by rules to avoid stalemate

if __name__ == "__main__":
	import doctest
	doctest.testmod()