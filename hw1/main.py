def maplist(fn, items):
	"""Exactly like map, but returns a list."""
	return list(map(fn, items))

def permute(items):
	"""
	Return all possible permutations of items.

	>>> permute([1, 2, 3])
	[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
	"""

	if len(items) == 0: return items
	if len(items) == 1: return [items]

	ret = []

	for x in items:
		ret = ret + [
			[x] + permuted for permuted in permute([y for y in items if y != x])
		]

	return ret


if __name__ == "__main__":
	permute([1, 2, 3])