#!/usr/bin/env python3
from typing import *
from enum import Enum
from random import Random
from dataclasses import dataclass
from abc import ABC, abstractmethod

# TODO: rename GameState to Turn
# TODO: I think it might be best to refactor this into a representation where there's a list of
#       token positions, from which is derived the board, etc.

# Question: a number of my functions don't have the same names as the ones perscribed. Is that OK?

class Player(Enum):
	"""
	An enum representing both options for players (Black and White).
	"""
	BLACK = 'BLACK'
	WHITE = 'WHITE'

	@property
	def swapped(self):
		return Player.BLACK if self == Player.WHITE else Player.WHITE

	@property
	def short_str(self):
		"""
		A very short (ie. one letter) symbol identifying the player, mostly used for debugging.
		"""
		return "B" if self == Player.BLACK else "W"
	
	@property
	def long_str(self):
		"""
		Human-readable name of this player.
		"""
		return "Black" if self == Player.BLACK else "White"


PositionState = Literal[-1, 0, 1] # -1 = opponent, 0 = no checker, 1 = our checker
"""
Represents one position on the board.

-1 = opponent's checker, 1 = our checker, 0 = empty
"""

BoardState = Tuple[PositionState, ...]
"""
Represents the board, relative to a player. Each element is one position. A player's checkers move
from left to right, meaning that the home is at position -1 and the goal is at position length + 1.

Obviously, the reverse is true for the opponent.
"""

@dataclass(frozen=True)
class GameConfiguration:
	"""
	A data class representing the particular variant of Nanon we're playing. Completely immutable.

	The defaults represent standard Nanon, with a 6 positions on the board, 3 checkers per player,
	and a standard six-sided die.
	"""

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

	This is just a wrapper around another Iterator to enable specifying a die_size.
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
	"""
	A dataclass representing the current state of the game. Completely immutable.
	"""

	player: Player
	""" Who's turn is it? """

	roll: int
	"""
	What did the current player roll?
	
	KLUDGE: Currently, roll can be negative so that a GameState can be losslessly swapped. I'm not
	sure if that's the right way to do it.
	"""

	# TODO: clarify if this is before or after the turn is taken
	board: BoardState
	""" What is the state of the board? """

	checkers_in_goal: Tuple[int, int] = (0, 0) # first item is ours, positive; second is theirs, negative
	""" How many checkers have been scored in the goal? """

	config: GameConfiguration = GameConfiguration()
	""" The configuration representing the variant of Nanon we're playing. """

	dicestream: Dicestream = Dicestream.random(die_size=config.die_size)
	"""
	The dicestream we're using. Importantly, this is only touched once at creation time when this
	turn's roll is calculated.
	"""

	def __post_init__(self):
		# Sanity Checks
		assert self.dicestream.die_size == self.config.die_size, "dicestream's die size must match game config's die_size!"
		assert abs(self.roll) <= self.config.die_size and abs(self.roll) >= 1, "roll must be in range [1, die_size]"


	def print_board(self):
		"""
        Print a human-readable view of the board.

        >>> GameState(player=Player.BLACK, roll=3, board=[0, 1, 0, 0, -1, 0], checkers_in_goal=(1, -1), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →                            
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |     ○        ●     |             
        Home → ○○○   |  ▲  ▲  ▲  ▲  ▲  ▲  |   ●●● ← Home
                                    ← White             
        >>> GameState(player=Player.BLACK, roll=3, board=[0, 0, 0, 0, 0, 0], checkers_in_goal=(0, 0), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →                            
        Goal →       |  ▼  ▼  ▼  ▼  ▼  ▼  |       ← Goal
                     |                    |             
        Home → ○○○○○ |  ▲  ▲  ▲  ▲  ▲  ▲  | ●●●●● ← Home
                                    ← White             
        >>> GameState(player=Player.BLACK, roll=3, board=[0, 0, 0, 0, 0, 0], checkers_in_goal=(5, -5), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →                            
        Goal → ●●●●● |  ▼  ▼  ▼  ▼  ▼  ▼  | ○○○○○ ← Goal
                     |                    |             
        Home →       |  ▲  ▲  ▲  ▲  ▲  ▲  |       ← Home
                                    ← White             
        >>> GameState(player=Player.BLACK, roll=3, board=[-1, 1, -1, 1, -1, 1], checkers_in_goal=(1, -1), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →                            
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |  ●  ○  ●  ○  ●  ○  |             
        Home → ○     |  ▲  ▲  ▲  ▲  ▲  ▲  |     ● ← Home
                                    ← White             
        """
		checker_symbols = {
			 0: ' ',
			 1: '○' if self.player == Player.BLACK else '●',
			-1: '○' if self.player == Player.WHITE else '●'
		}
		board_checkers = '|  ' +  '  '.join([checker_symbols[checker] for checker in self.board]) + '  |'


		board_top = '| ' + ' ▼ ' * self.config.board_size + ' |'
		board_bottom = '| ' + ' ▲ ' * self.config.board_size + ' |'

		# NOTE: left_top/left_bottom and right_top/right_bottom are the same length
		left_top = 'Goal → ' + (checker_symbols[-1] * -self.checkers_in_goal[1]).ljust(self.config.checkers_per_player, ' ') + ' '
		right_top = ' ' + (checker_symbols[1] * self.checkers_in_goal[0]).rjust(self.config.checkers_per_player, ' ') + ' ← Goal'

		left_bottom = 'Home → ' + (checker_symbols[1] * self.checkers_at_home[0]).ljust(self.config.checkers_per_player, ' ') + ' '
		right_bottom = ' ' + (checker_symbols[-1] * -self.checkers_at_home[1]).rjust(self.config.checkers_per_player, ' ') + ' ← Home'

		top_line = left_top + board_top + right_top
		bottom_line = left_bottom + board_bottom + right_bottom

		line_len = len(bottom_line)

		mid_line = ((' ' * len(left_bottom)) + board_checkers).ljust(line_len, ' ')

		print(((' ' * len(left_top)) + self.player.long_str + ' →').ljust(line_len, ' '))
		print(top_line)
		print(mid_line)
		print(bottom_line) 
		print(('← ' + self.player.swapped.long_str + (' ' * len(right_bottom))).rjust(line_len, ' '))
	

	@property
	def checkers_on_board(self) -> Tuple[int, int]: # first item is ours, positive; second is theirs, negative
		"""
		Return the number of checkers on the board for each player. The first element is a positive
		number representing the number of checkers we have, the second is a negative number
		representing the number our opponent has.

		We derive this information from the board itself to avoid inconsistent states.

		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, 0, 0, -1, 0], checkers_in_goal=(1, -1)).checkers_on_board
		(1, -1)
		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, 0, 0, -1, 0], checkers_in_goal=(0, 0)).checkers_on_board
		(1, -1)
		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, -1, 1, -1, 0], checkers_in_goal=(0, 0)).checkers_on_board
		(2, -2)
		"""
		return (self.board.count(1), -self.board.count(-1))


	@property
	def checkers_at_home(self) -> Tuple[int, int]: # first item is ours, positive; second is theirs, negative
		"""
		Return the number of checkers at home for each player. The first element is a positive
		number representing the number of checkers we have, the second is a negative number
		representing the number our opponent has.

		We derive this information to avoid inconsistent states.

		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, 0, 0, -1, 0], checkers_in_goal=(1, -1)).checkers_at_home
		(1, -1)
		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, 0, 0, -1, 0], checkers_in_goal=(0, 0)).checkers_at_home
		(2, -2)
		>>> GameState(player=Player.BLACK, roll=3, board=[0, 1, -1, 1, -1, 0], checkers_in_goal=(0, 0)).checkers_at_home
		(1, -1)
		"""
		return (
			self.config.checkers_per_player - self.checkers_on_board[0] - self.checkers_in_goal[0],
			-self.config.checkers_per_player - self.checkers_on_board[1] - self.checkers_in_goal[1]
		)
	

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
	# Run all the unit tests
	failures, tests = doctest.testmod()
	if failures == 0 and tests > 0:
		print("Tests Passed!")