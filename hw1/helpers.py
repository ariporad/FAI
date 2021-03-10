"""
This file contains a number of helper utilities that are neither particularly interesting, but are
needed. None contain any domain knowledge.
"""

def permute(items):
	"""
	Lazily produce all possible permutations of items.

	NOTE: The list of items itself is not processed lazily (that wouldn't really make any sense),
	but the list of permutations is generated lazily. (So it's safe to call this function with quite
	large values for `item`)

	>>> list(permute([1]))
	[(1,)]
	>>> list(permute([1, 2, 3]))
	[(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
	"""

	for item in items:
		# For some reason, filter doesn't actually work lazily here. However, the list of items is
		# never really that big, so it's perfectly fine to force it to be eager, which does work
		others = [a for a in items if a != item]

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
	Deduplicate an iterator, lazily. Items will be emitted in the order of `items`, except that
	duplicate values will be skipped. Values must be hashable.

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
	A lazy interator-based stack.

	NOTE: Due to the nature of python iterators, this stack yields each iterator's items in order.
	However, the iterators themselves go in stackwise order

	>> stack = LazyStack([1, 2, 3])
	>> for i in stack:
	>>   if i == 1: stack.push([4, 5, 6])
	>>	  print(i)
	1
	4
	5
	6
	2
	3
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

# CITATION: This class is heavily adapted from https://stackoverflow.com/a/3160819. Since a progress
# bar was completely unrelated to the point of this assignment, I felt it was acceptable and
# appropriate to not write the functionality muself.
class ProgressBar:
	"""
	A command-line progress bar.
	"""

	def __init__(self, width = 50, progress = 0):
		"""
		Create a progress bar. This writes it to the console.
		"""

		self.width = 40
		self.progress = progress
		self.last_status = ""
		self.update(progress, skip_erase=True)
	
	def update(self, progress, status = "", skip_erase=False):
		"""
		Update the progress bar, rewriting it to the console.
		"""

		self.progress = progress

		print(f"\r[{'█' * round(self.width * self.progress)}{' ' * round(self.width * (1 - self.progress))}] {status}{' ' * (max(0, len(self.last_status) - len(status)))}", end="", flush=True)

		self.last_status = status

	def stop(self, status = ""):
		"""
		Erase the progress bar from the console.
		"""
		print(f"\r{' ' * (self.width + 3 + len(self.last_status))}\r{status}", end=("\n" if status else ""), flush=True)
		self.last_status = status



