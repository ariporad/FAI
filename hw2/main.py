#!/usr/bin/env python3
from typing import *
from enum import Enum
from random import Random
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Question: a number of my functions don't have the same names as the ones perscribed. Is that OK?

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

@dataclass(frozen=True)
class GameConfiguration:
	board_size: int = 6
	checkers_per_player: int = 3
	die_size: int = 6

	def __post_init__(self):
		# Sanity Check
		assert self.checkers_per_player < self.die_size, "checkers per player must be less than die size to avoid stalemates"
	
	def __str__(self):
		return f"{{{self.board_size},{self.checkers_per_player},{self.die_size}}}"


class Dicestream(Iterator[int]):
	"""
	An iterator representing a stream of dice rolls. Each roll is an integer between 1 and die_size,
	inclusive.
	"""

	die_size: int
	_iterator: Iterator[int]

	def __init__(self, iterable: Iterable[int], die_size: int = 6):
		self.die_size = die_size
		self._iterator = iter(iterable)

	def __next__(self) -> int:
		return next(self._iterator)

	@classmethod
	def random(cls, die_size: int = 6, seed: int = None) -> 'Dicestream':
		"""
		Return a dicestream that produces uniformly random rolls.
		
		>>> dicestream = Dicestream.random(die_size = 6, seed = 1) # deterministic because seed is specified
		>>> next(dicestream)
		2
		>>> next(dicestream)
		5
		>>> next(dicestream)
		1
		>>> next(dicestream)
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


def first_roll(dicestream: Dicestream) -> int:
	"""
	Calculate the first roll of the game, as follows: two dice are rolled, and the difference is
	returned. In the event of a tie, re-roll the dice. This may result in either a positive or
	negative number, which should be interpreted as in favor of one player or another. Which player
	is which doesn't matter, by definition.

	>>> first_roll(Dicestream.fixed([1, 5]))
	-4
	>>> first_roll(Dicestream.fixed([2, 2, 3, 3, 4, 2]))
	2
	"""
	diff = next(dicestream) - next(dicestream)

	if diff == 0:
		return first_roll(dicestream)

	return diff


@dataclass(frozen=True)
class GameState:
	player: Player
	roll: int
	board: BoardState
	checkers_in_goal: Tuple[int, int] = (0, 0) # first item is ours, positive; second is theirs, negative
	config: GameConfiguration = GameConfiguration()
	dicestream: Dicestream = Dicestream.random(die_size=config.die_size)

	def __post_init__(self):
		assert self.dicestream.die_size == self.config.die_size, "dicestream's die size must match game config's die_size!"
		# KLUDGE: Currently, roll can be negative so that a GameState can be losslessly swapped. I'm
		# not sure if that's the right way to do it.
		assert abs(self.roll) <= self.config.die_size and abs(self.roll) >= 1, "roll must be in range [1, die_size]"
	
	@property
	def checkers_on_board(self) -> Tuple[int, int]: # first item is ours, positive; second is theirs, negative
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
		return f"<GameState{self.config} {self.player.short_str}{self.roll} {self.checkers_in_goal[1]}[{''.join(map(format_position, self.board))}]{self.checkers_in_goal[0]}>"


	@property
	def swapped(self):
		"""
		Return the same game, but from the other player's perspective. This allows most logic to
		only be written for one player.

		>>> print(GameState(Player.BLACK, 3, [1, 1, -1, 0, 0, 0], (0, -1)).swapped)
		<GameState{6,3,6} W-3 0[___+--]1>
		"""
		def swap(some_tuple: Tuple[int, ...]) -> Tuple[int, ...]:
			return tuple(reversed([-value for value in some_tuple]))

		return GameState(
			config=self.config,
			roll=-self.roll,
			player=self.player.swapped,
			board=swap(self.board),
			checkers_in_goal=swap(self.checkers_in_goal)
		)
	
	@property
	def winner(self):
		"""
		Return the winner (1 if it's us, -1 if it's not), or nil if there is no winner.
		
		A player wins when they've gotten all their checkers off the board.

		>>> GameState(Player.BLACK, 4, [-1, -1, 0, 0, 0, 0], (3, -1)).winner
		1
		>>> GameState(Player.WHITE, 4, [1, 1, 0, 0, 0, 0], (1, -3)).winner
		-1
		>>> GameState(Player.BLACK, 4, [1, 1, 0, 0, 0, -1], (1, -2)).winner
		0
		"""
		if self.checkers_in_goal[0] == self.config.checkers_per_player:
			return 1
		elif self.checkers_in_goal[1] == -self.config.checkers_per_player:
			return -1
		else:
			return 0


def start_game(dicestream: Dicestream = None, config: GameConfiguration = GameConfiguration(), seed: int = None):
	"""
	Create a starting game state.
	>>> print(start_game(Dicestream.fixed([1, 2])))
	<GameState{6,3,6} W1 0[++__--]0>
	>>> print(start_game(Dicestream.fixed([1, 2]), config=GameConfiguration(6, 3, 6)))
	<GameState{6,3,6} W1 0[++__--]0>
	>>> print(start_game(Dicestream.fixed([1, 2]), config=GameConfiguration(7, 4, 6)))
	<GameState{7,4,6} W1 0[++___--]0>
	>>> print(start_game(Dicestream.fixed([1, 2]), config=GameConfiguration(8, 3, 6)))
	<GameState{8,3,6} W1 0[++____--]0>
	>>> print(start_game(Dicestream.fixed([1, 2]), config=GameConfiguration(8, 4, 6)))
	<GameState{8,4,6} W1 0[+++__---]0>
	"""
	if dicestream is None:
		dicestream = Dicestream.random(config.die_size, seed)
	else:
		assert seed is None, "seed cannot be provided if dicestream is provided"

	starting_roll = first_roll(dicestream)
	starting_player = Player.BLACK
	if starting_roll < 0:
		starting_roll *= -1
		starting_player = Player.WHITE
	
	# TODO: the spec is unclear as to the starting configuration for size > 6
	checkers_start_on_board = min(config.checkers_per_player - 1, (config.board_size // 2) - 1)
	blank_spaces = config.board_size - (checkers_start_on_board * 2)
	board = ((1,) * checkers_start_on_board) + ((0,) * blank_spaces) + ((-1,) * checkers_start_on_board)

	initial_state = GameState(starting_player, starting_roll, board, config=config, dicestream=dicestream)

	return initial_state


if __name__ == "__main__":
	import doctest
	failures, tests = doctest.testmod()
	if failures == 0 and tests > 0:
		print("Tests Passed!")