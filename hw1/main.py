def maplist(fn, items):
	"""Exactly like map, but returns a list."""
	return list(map(fn, items))

def permute(items):
	"""
	Return all possible permutations of items.

	>>> permute([1, 2, 3])
	[(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
	"""

	if len(items) == 0: return items
	if len(items) == 1: return [tuple(items)]

	ret = []

	for x in items:
		ret = ret + [
			tuple((x,) + permuted) for permuted in permute([y for y in items if y != x])
		]

	return ret

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
	Deduplicate a list. No guarantees are made about order.

	>>> unique([1, 2, 3, 3, 1])
	[1, 2, 3]
	"""
	# HACK: This is a fast and easy implementation, even if it's a little ugly
	return list(set(items))

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
	return unique(map(canonicalize_nut, permute(range(1, n + 1))))[0:n+1]

if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print(generate_puzzle(6))