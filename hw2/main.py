#!/usr/bin/env python3
from typing import *
from enum import Enum
from random import Random
from dataclasses import dataclass
from abc import ABC, abstractmethod

class Player(Enum):
	BLACK = 'BLACK'
	WHITE = 'WHITE'

	@property
	def swapped(self):
		return Player.BLACK if self == Player.WHITE else Player.WHITE

	@property
	def short_str(self):
		return "B" if self == Player.BLACK else "W"


PositionState = Literal[-1, 0, 1] # -1 = opponent, 0 = no checker, 1 = our checker
BoardState = Tuple[PositionState, ...]

@dataclass
class GameConfiguration:
	board_size: int = 6
	checkers_per_player: int = 3
	die_size: int = 6

	def __post_init__(self):
		# Sanity Check
		assert self.checkers_per_player < self.die_size, "checkers per player must be less than die size to avoid stalemates"
	
	def __str__(self):
		return f"{{{self.board_size},{self.checkers_per_player},{self.die_size}}}"

@dataclass(frozen=True)
class GameState:
	player: Player
	board: BoardState
	checkers_in_goal: Tuple[int, int] = (0, 0) # first item is ours, positive; second is theirs, negative
	config: GameConfiguration = GameConfiguration()
	
	@property
	def checkers_on_board(self) -> Tuple[int, int]: # first item is ours, positive; second is theirs, negative
		# TODO: memoize against board
		return (self.board.count(1), -self.board.count(-1))

	@property
	def checkers_at_home(self) -> Tuple[int, int]: # first item is ours, positive; second is theirs, negative
		return tuple([
			self.config.checkers_per_player - on_board - in_goal
			for on_board, in_goal
			in zip(self.checkers_on_board, self.checkers_in_goal)
		])
	
	def __str__(self):
		def format_position(pos):
			if pos == 1:
				return "+"
			elif pos == -1:
				return "-"
			else:
				return "_"
		return f"<GameState{self.config} {self.player.short_str} {self.checkers_in_goal[1]}[{''.join(map(format_position, self.board))}]{self.checkers_in_goal[0]}>"


	@property
	def swapped(self):
		"""
		Return the same game, but from the other player's perspective. This allows most logic to
		only be written for one player.

		>>> print(GameState(Player.BLACK, [1, 1, -1, 0, 0, 0], (0, -1)).swapped)
		<GameState{6,3,6} W 0[___+--]1>
		"""
		def swap(some_tuple: Tuple[int, ...]) -> Tuple[int, ...]:
			return tuple(reversed([-value for value in some_tuple]))

		return GameState(
			config=self.config,
			player=self.player.swapped,
			board=swap(self.board),
			checkers_in_goal=swap(self.checkers_in_goal)
		)




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
	config: GameConfiguration
	dicestream: Iterator[int]

	def __init__(self, dicestream: Iterator[int] = None, config: GameConfiguration = GameConfiguration(), seed: int = None):

		if dicestream is None:
			dicestream = Dicestream.random(config.die_size, seed)
		else:
			assert seed is None, "seed cannot be provided if dicestream is provided"

		assert dicestream.die_size == config.die_size, "dicestream's die size must match game config's die_size!"

		self.config = config
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