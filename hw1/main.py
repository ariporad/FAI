from itertools import islice

class Solution:
	"""
	Class representing a (possibly-incomplete) solution to the problem.

	This class is heavily context-dependent, and the user is expected to know what's going on with
	it. To that end, it doesn't store things like order (number of sides to each nut), completeness,
	etc. This is for simplicity.
	"""

	def __init__(self, center_nut, nuts_to_place, placed_nuts = []):
		# The center nut and nuts_to_place are specified as in the canonical format (see
		# `canonicalize_nut`). 
		self.center_nut = center_nut
		self.nuts_to_place = nuts_to_place

		# Each index `i` is the nut that's placed on the edge `i` of the center nut (ie. aligned
		# with the number at `self.center_nut[i]`). These nuts are rotated such that their first
		# element is the one touching the center nut.
		self.placed_nuts = placed_nuts

	def is_invalid(self):
		"""
		Validate that the solution doesn't break any rules. **DOES NOT** ensure that the solution is
		complete, so as to enable validating partial solutions. (ie. you should call both is_valid
		and is_complete to ensure the puzzle is solved.)

		Returns a string explaining (one of the reason(s)) why the solution is invalid, or False if
		the solution is valid.
		"""
		for i, nut in enumerate(self.placed_nuts):
			# First, check the center connection
			if self.center_nut[i] != nut[0]:
				return f"Center[{i}] = {self.center_nut[i]} != nut[{i}][0] = {nut[0]}"

			# Then, check the nut's neighbor. We only check one neighbor per nut (the one with the
			# next index/clockwise), because if all the nuts are in place this will result in all
			# the connections being checked exactly once.

			next_nut_i = (i + 1) % len(self.placed_nuts)
			if not self.placed_nuts[next_nut_i]: continue # If the next nut hasn't been placed
			if self.placed_nuts[next_nut_i][1] != nut[-1]:
				return f"Edge: nut[{i + 1}][0] = {self.placed_nuts[next_nut_i][0]} != nut[{i}][-1] = {nut[-1]}"

		return False

	def is_complete(self):
		"""
		Validate that the solution is complete (ie. all nuts are placed). **DOES NOT** ensure that
		no rules have been broken. (ie. you should call both is_valid and is_complete to ensure the
		puzzle is solved.)

		>>> solution = Solution((1, 2, 3), [], [(1, 2, 3), (2, 3, 1), (3, 1, 2)])
		>>> solution.is_complete()
		True
		>>> solution.is_invalid()
		False
		"""
		return len(self.nuts_to_place) == 0 and len(self.placed_nuts) == len(self.center_nut)


def maplist(fn, items):
	"""Exactly like map, but returns a list."""

	return list(map(fn, items))

def log(title, value):
	"""
	For debugging purposes, print out a value (with a description) then return the value. This
	allows it to be inserted into expressions:
	
	>>> 5 + log("magic number:", 5)
	magic number: 5
	10
	"""

	print(title, value)
	return value

def permute(items):
	"""
	Lazily produce all possible permutations of items.

	>>> list(permute([1]))
	[(1,)]
	>>> list(permute([1, 2, 3]))
	[(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
	"""

	for item in items:
		# For some reason, filter doesn't actually work lazily here. However, the list of items is
		# never really that big, so it's perfectly fine to force it to be eager, which does work
		others = list(filter(lambda a: a != item, items))

		# We have to use this variable to track if permute(others) actually returned anything (it
		# won't iff there's only one item left. If it didn't return anything, then the loop will
		# never execute, but we do need to yield something so that the current item is carried up.
		had_rest = False
		for rest in permute(others):
			had_rest = True
			yield (item, *rest)

		if not had_rest:
			yield (item,)


def rotate(items, num):
	"""
	Rotate a list or tuple.

	>>> rotate([1, 2, 3, 4, 5], 3)
	[4, 5, 1, 2, 3]
	>>> rotate((1, 2, 3, 4, 5), 3)
	(4, 5, 1, 2, 3)
	"""
	return items[num:] + items[:num]

def unique(items):
	"""
	Deduplicate an iterator, lazily. No guarantees are made about order. Values must be hashable.

	>>> list(unique([1, 2, 3, 3, 1]))
	[1, 2, 3]
	>>> list(unique([(1, 2), (2, 3), (2, 3), (1, 2)]))
	[(1, 2), (2, 3)]
	"""

	already_seen = set()

	for item in items:
		if item in already_seen:
			continue
		else:
			already_seen.add(item) 
			yield item



def canonicalize_nut(nut):
	"""
	Rotate a nut such that 1 is first. The elements in the list are in clockwise order.

	>>> canonicalize_nut((4, 5, 6, 1, 2, 3))
	(1, 2, 3, 4, 5, 6)
	"""

	return rotate(nut, nut.index(1))


def generate_puzzle(n):
	"""
	Generate a nuts-style puzzle of n+1 n-sided regular polygons with a number 1 through n on each
	side.
	"""

	numbers = range(1, n + 1)
	all_nuts = permute(numbers)
	all_nuts_canonicalized = map(canonicalize_nut, all_nuts)
	all_nuts_unique = unique(all_nuts_canonicalized)

	puzzle = islice(all_nuts_unique, n + 1)

	return puzzle

if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print(list(generate_puzzle(6)))