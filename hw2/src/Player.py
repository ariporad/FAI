from typing import *
from enum import Enum

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

	def int_value(self):
		return 1 if self == Player.BLACK else 2

	def __repr__(self):
		return "Player.BLACK" if self == Player.BLACK else "Player.WHITE"
