from random import shuffle
from time import perf_counter
from helpers import permute, rotate, unique, LazyStack, ProgressBar

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
	all_nuts = map(canonicalize_nut, all_nuts)
	all_nuts = unique(all_nuts)
	all_nuts = list(all_nuts)

	shuffle(all_nuts)

	return all_nuts[0:n + 1]


class State:
	"""
	Class representing a (possibly-incomplete) solution to the problem.

	This class is heavily context-dependent, and the user is expected to know what's going on with
	it. To that end, it doesn't store things like order (number of sides to each nut), completeness,
	etc. This is for simplicity.
	"""

	def __init__(self, center_nut, nuts_to_place, placed_nuts = []):
		# Calculate the order of this puzzle
		self.n = len(center_nut) if center_nut else len(nuts_to_place[0])

		# Fill placed_nuts with a bunch of placeholder Nones to avoid index-out-of-bounds errors
		while len(placed_nuts) < self.n:
			placed_nuts.append(None)

		# The center nut and nuts_to_place are specified as in the canonical format (see
		# `canonicalize_nut`). 
		self.center_nut = center_nut
		self.nuts_to_place = nuts_to_place

		# Each index `i` is the nut that's placed on the edge `i` of the center nut (ie. aligned
		# with the number at `self.center_nut[i]`). These nuts are rotated such that their first
		# element is the one touching the center nut.
		self.placed_nuts = placed_nuts

	def __str__(self):
		return f"<State is_invalid={self.is_invalid()} is_complete={self.is_complete()}\n\tcenter={self.center_nut}\n\tplaced_nuts={self.placed_nuts}\n\tnuts_to_place={self.nuts_to_place}\n>"

	def is_invalid(self):
		"""
		Validate that the solution doesn't break any rules. **DOES NOT** ensure that the solution is
		complete, so as to enable validating partial solutions. (ie. you should call both is_valid
		and is_complete to ensure the puzzle is solved.)

		Returns a string explaining (one of the reason(s)) why the solution is invalid, or False if
		the solution is valid.
		"""
		if not self.center_nut:
			return False if all(map(lambda x: x is None, self.placed_nuts)) else "No center nut but some nuts have been placed!"

		for i, nut in enumerate(self.placed_nuts):
			if nut is None: continue # Don't process nonexistant nuts

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

		>>> state = State((1, 2, 3), [], [(1, 2, 3), (2, 3, 1), (3, 1, 2)])
		>>> state.is_complete()
		True
		>>> state.is_invalid()
		False
		"""
		return self.center_nut is not None and \
			len(self.nuts_to_place) == 0 and \
			len(self.placed_nuts) == self.n and \
			all(map(lambda x: x is not None, self.placed_nuts))
	
	def next_states(self):
		# Invalid states have no next states
		if self.is_invalid():
			return []

		# If it's complete, then there are no possible next states
		if self.is_complete():
			return []

		# If there's no center nut, then the next states are just using every possible nut as the center
		if not self.center_nut:
			yield from map(
				lambda center: State(center, [nut for nut in self.nuts_to_place if nut != center], []),
				self.nuts_to_place
			)
			return

		# Otherwise, the possible states are putting every nut in every open slot, except where that
		# would be an invalid state.
		for i in range(len(self.center_nut)):
			if self.placed_nuts[i]: continue # Can't put a nut here if there already is one

			for nut in self.nuts_to_place:
				others_to_place = [n for n in self.nuts_to_place if n != nut]
				new_placed = self.placed_nuts.copy()

				nut_rotated = rotate(nut, nut.index(self.center_nut[i]))
				new_placed[i] = nut_rotated

				possible_state = State(self.center_nut, others_to_place, new_placed)

				if possible_state.is_invalid():
					continue

				yield possible_state

			# We only want to generate states for the next open nut slot, because we have to put
			# something there eventually and so there's no point in generating states for all the
			# other slots yet.
			break


def solve_puzzle(nuts, all=False):
	"""
	Given a list of valid nuts, return a State representing the solution to the puzzle (or None if
	it's unsolvable).

	>>> TEST_PUZZLE = [ # Actual test puzzle as mandated by the assignment
	... 	(1, 6, 5, 4, 3, 2),
	... 	(1, 6, 4, 2, 5, 3),
	... 	(1, 2, 3, 4, 5, 6),
	... 	(1, 6, 2, 4, 5, 3),
	... 	(1, 4, 3, 6, 5, 2),
	... 	(1, 4, 6, 2, 3, 5),
	... 	(1, 6, 5, 3, 2, 4),
	... ]
	>>> solution = solve_puzzle(TEST_PUZZLE)
	>>> solution.is_invalid()
	False
	>>> solution.is_complete()
	True
	>>> print(solution) # doctest: +NORMALIZE_WHITESPACE
	<State is_invalid=False is_complete=True
        center=(1, 6, 2, 4, 5, 3)
        placed_nuts=[(1, 4, 6, 2, 3, 5), (6, 5, 3, 2, 4, 1), (2, 1, 4, 3, 6, 5), (4, 5, 6, 1, 2, 3), (5, 3, 1, 6, 4, 2), (3, 2, 1, 6, 5, 4)]
        nuts_to_place=[]
	>

	>>> TEST_PUZZLE_EXTRA = [ # Additional test puzzle, known to be solvable
	... 	(1, 2, 0, 4, 3, 5),
	... 	(5, 2, 3, 1, 0, 4),
	... 	(5, 2, 0, 3, 4, 1),
	... 	(4, 2, 5, 0, 3, 1),
	... 	(4, 2, 0, 3, 1, 5),
	... 	(3, 2, 5, 1, 4, 0),
	... 	(4, 2, 1, 0, 3, 5)
	... ]
	>>> solution = solve_puzzle(TEST_PUZZLE)
	>>> solution.is_invalid()
	False
	>>> solution.is_complete()
	True
	>>> print(solution) # doctest: +NORMALIZE_WHITESPACE
	<State is_invalid=False is_complete=True
        center=(1, 6, 2, 4, 5, 3)
        placed_nuts=[(1, 4, 6, 2, 3, 5), (6, 5, 3, 2, 4, 1), (2, 1, 4, 3, 6, 5), (4, 5, 6, 1, 2, 3), (5, 3, 1, 6, 4, 2), (3, 2, 1, 6, 5, 4)]
        nuts_to_place=[]
	>
	"""

	state = State(None, nuts, [])

	stack = LazyStack([state])

	solutions = []

	for state in stack:
		is_invalid = state.is_invalid()
		is_complete = state.is_complete()
		next_states = state.next_states()
		
		if is_invalid: continue
		if is_complete: # implicitly isn't invalid from above
			# We've found a solution!
			if all:
				solutions.append(state)
			else:
				return state
		stack.push(next_states)
	
	if all: # we've explored everything
		return solutions
	else: # if we're not looking for every solution, then getting here means we didn't find one
		return None


TEST_PUZZLE = [
	(1, 6, 5, 4, 3, 2),
	(1, 6, 4, 2, 5, 3),
	(1, 2, 3, 4, 5, 6),
	(1, 6, 2, 4, 5, 3),
	(1, 4, 3, 6, 5, 2),
	(1, 4, 6, 2, 3, 5),
	(1, 6, 5, 3, 2, 4),
]


def test_solvability(n, count_solutions=True, rounds=1000):
	"""
	Generate `rounds` random puzzles of degree `n`, and check how many of them have solutions.
	
	Prints status to the console, and returns the ratio that were solvable.
	"""

	print(f"Testing solvability of n = {n} by generating {rounds} random puzzles and seeing how many are solvable.")

	progress = ProgressBar()

	solvable = 0
	num_solutions = [0, 0, 0] # zero solutions, one solution, more than one solution
	very_solvable = [] # tuples: (solution_count, state, solutions)
	start_time = perf_counter()

	for i in range(rounds):
		puzzle = list(generate_puzzle(n))
		solution = solve_puzzle(puzzle, all=count_solutions)

		if solution:
			solvable = solvable + 1
		
		if count_solutions:
			solution_count = min(2, len(solution))
			num_solutions[solution_count] = num_solutions[solution_count] + 1
			if solution_count == 2:
				very_solvable.append((solution_count, puzzle, solution))


		time_estimate = ((perf_counter() - start_time) / (i + 1)) * (rounds - (i + 1))
		progress.update((i + 1)/rounds, f"{(i + 1):0004}/{rounds} ({round(time_estimate)}s left): {'Solvable' if solution else 'Unsolvable'}")

	progress.stop(f"Done. {round(100 * solvable/rounds)}% Solvable ({solvable}/{rounds}) for n = {n}")

	if count_solutions:
		print(f"{num_solutions[0]} with 0 solutions, {num_solutions[1]} with 1 solution, {num_solutions[2]} with 2+ solutions (max: {max([num for num, _, _ in very_solvable])}).")

	return solvable/rounds


def main():
	print("Ari Porad's Solution for Homework 1, Drive Ya Nuts:")
	state = solve_puzzle(TEST_PUZZLE)
	print(f"Solution Found: {state}" if state else "Couldn't find a solution!")

	# What follows isn't the cleanest way I've ever seen to print out a n = 6 puzzle, but it's
	# simple and it works.
	nc = state.center_nut
	n0 = state.placed_nuts[0]
	n1 = state.placed_nuts[1]
	n2 = state.placed_nuts[2]
	n3 = state.placed_nuts[3]
	n4 = state.placed_nuts[4]
	n5 = state.placed_nuts[5]

	print(f"""
    {n5[3]} {n5[4]}     {n0[2]} {n0[3]}     
   {n5[2]}   {n5[5]}   {n0[1]}   {n0[4]}    
    {n5[1]} {n5[0]}     {n0[0]} {n0[5]}     
                          
 {n4[4]} {n4[5]}     {nc[5]} {nc[0]}     {n1[1]} {n1[2]} 
{n4[3]}   {n4[0]}   {nc[4]}   {nc[1]}   {n1[0]}   {n1[3]} 
 {n4[2]} {n4[1]}     {nc[3]} {nc[2]}     {n1[5]} {n1[4]}  
                      
    {n3[5]} {n3[0]}      {n2[0]} {n2[1]}     
   {n3[4]}   {n3[1]}    {n2[5]}   {n2[2]}    
    {n3[3]} {n3[2]}      {n2[4]} {n2[3]}     
	""")


if __name__ == "__main__":
	import doctest
	doctest.testmod()

	test_solvability(7)


	# puzzle = list(generate_puzzle(5))

	# print("Randomly Generated Puzzle:", puzzle)
	# print("Solving...")
	# solution = solve_puzzle(puzzle)
	# print(f"Found a Solution: {solution}" if solution else "Couldn't find a solution! Puzzle is unsolvable!")

	# main()