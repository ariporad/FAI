#!/usr/bin/env python3
from typing import *
from random import Random
from abc import ABC, abstractmethod

PositionState = Literal[-1, 0, 1] # -1 = opponent, 0 = no checker, 1 = our checker
GameState = Tuple[PositionState, ...]

class Dicestream(Iterator[int]):
	die_size: int
	_iterator: Iterator[int]

	def __init__(self, iterable: Iterable[int], die_size: int = 6):
		self.die_size = die_size
		self._iterator = iter(iterable)

	def __next__(self) -> int:
		return next(self._iterator)

	@classmethod
	def random(cls, die_size: int = 6, seed: int = None) -> 'Dicestream':
		def random_iterator():
			random = Random(seed)
			
			while True:
				yield random.randint(1, die_size)
			
		return cls(random_iterator(), die_size)

	@classmethod
	def fixed(cls, rolls: List[int], die_size: int = 6) -> 'Dicestream':
		assert all([1 <= item and item <= die_size for item in rolls]), "all rolls must be in range [1, die_size]"
			
		return cls(rolls, die_size)



class Game:
	board_size: int
	checkers_per_player: int
	die_size: int
	dicestream: Iterator[int]

	def __init__(self, dicestream: Iterator[int] = None, board_size: int = 6, checkers_per_player: int = 3, die_size: int = 6, seed: int = None):
		# Sanity Check
		assert checkers_per_player < die_size, "checkers per player must be less than die size to avoid stalemates"

		if dicestream is None:
			dicestream = Dicestream.random(die_size, seed)
		else:
			assert seed is None, "seed cannot be provided if dicestream is provided"

		assert dicestream.die_size == die_size, "dicestream's die size must match game's die_size!"

		self.board_size = board_size
		self.checkers_per_player = checkers_per_player
		self.die_size = die_size
		self.dicestream = dicestream


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
		return next(self.dicestream)


	def first_roll(self):
		"""
		Calculate the first roll of the game, as follows: two dice are rolled, and the difference is
		returned. In the event of a tie, re-roll the dice.

		>>> game = Game(Dicestream.fixed([1, 5]))
		>>> game.first_roll()
		4
		>>> game = Game(Dicestream.fixed([2, 2, 3, 3, 4, 2]))
		>>> game.first_roll()
		2
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