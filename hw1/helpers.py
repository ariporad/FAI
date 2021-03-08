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


class LazyStack:
	"""
	A lazy interator-based queue.

	>> queue = LazyQueue([1, 2, 3])
	>> for i in queue:
	>>   if i == 1: queue.push([4, 5, 6])
	>>	  print(i)
	1
	2
	3
	4
	5
	6
	"""

	def __init__(self, iterator):
		self.iterators = []
		self.push(iterator)

	def __iter__(self):
		while True:
			if len(self.iterators) == 0: return

			try:
				yield next(self.iterators[-1])
			except StopIteration:
				self.iterators.pop()
				continue

	def push(self, iterator):
		self.iterators.append(iter(iterator))

