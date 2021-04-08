from typing import *
from random import Random

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