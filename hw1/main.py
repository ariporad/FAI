from itertools import islice

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
	Rotate a nut such that 1 is first.

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