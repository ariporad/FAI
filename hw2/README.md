# FAI Homework 2: Nannon

### By Ari Porad

# Introduction

I originally wrote this project for Brandeis University's COSI 101A _Fundamentals of Artificial Intelligence_ in Spring 2021 (referred to by me and me alone as the Olin-eqsue _FAI_, pronounced _/faye/_).

The assignment revolved around building an algorithm to play the game [Nannon](https://nannon.net), a simplified version of Backgammon. More generally, Nannon is parameterized into a family of games by three parameters: board size, number of checkers per player, and dice size. Standard Nannon is Nannon{6,3,6}.

![Nannon Rules](nannon-rules.png)

Most of the contents of this document can also be found in the original report that I turned in, which also includes some example program output ([Jupyter Notebook](src/report.ipynb), [PDF](report.pdf)). Additionally, the thoroughly-documented source code can be found in this repo (the most interesting bits can be found in [Board.py](src/Board.py) and [players.py](src/players.py)). Some discussion of my approach follows.

## Overview

For this assignment, I built an implementation of the game Nannon and several different algorithms that could play it--the most interesting of which is the knowledge-based player, which attempts to use handcrafted heuristics to pick the best move. I'll discuss the highlights here, and more details can be found in [the report](report.pdf) or in the thoroughly-documented code.

### Board Representation

I'm a big believer that if you choose your data structures right, the rest of your program writes itself. (That's a rough quote from someone, but I can't remember who.) To that end, I spent a substantial amount of time during this project iterating on my data structures. Originally, I stored the board as a list, where each item in the list represented a position on the board. Legal values were `0` (spot is empty), `1` (current player's checker), and `-1` (opponent's checker). Checkers in the home and goal zones were stored separately. That data structure was simple, which was nice. However, it was easy to get into an illegal state (wrong number of checkers), which I didn't like--a good data structure is one that can't represent an illegal state, after all. It was also hard to manipulate, with lots of loops looking for checkers. I ultimately decided to switch to a representation with an (unordered) list of `Checker`s, each of which has a `Player` (black or white) and a `Position`. Initially, I attempted to have each checker's position be relative _to that checker's home_, which meant that the representation was entirely perspective-independent. That ended up being too complicated to manage, so I settled on a perspective-dependent representation where all checker positions are measured relative to one player's (the perspective player's) home. I'm still not satisfied with this representation--it simultaneously feels a little too complicated, while also needing too much perspective swapping--but it's good enough. As they say, premature optimization is the root of all evil.

The list of checkers (which is always `2 * checkers_per_player` long) is encapsulated by a `Board`, which also tracks the perspective (if the perspective is Black, then lower indexes are closer to Black's home and vis versa) and `GameConfiguration` (the variant of Nannon, such as `{6,3,6}` or `{8,4,6}`). `Board` contains much of the game logic, including calculating open spots, legal `Move`s, and the winner. The `Move` class tracks a possible move, and is responsible for properly executing it and returning the resulting `Board`. Finally, the `Dicestream` class wraps various iterators that can provide a stream of dice rolls.

### Knowledge-Based Player

My knowledge-based Nannon player ended up somewhat similar to the score-based player that was prescribed by the assignment (which performs a minimax search, picking the move where the current player's pieces are as far along as possible and the opponent's pieces are as close to their home as possible). However, there are some key differences. It's built by assigning "points" to different aspects of each possible move. It then picks the move with the highest total point value.

The algorithm's guiding principles are:

-   Checkers closer to the goal are better
-   Knocking off an opponent's checker is valuable, especially if it's close to the goal
-   Using a roll of 6 to move a checker that's 1 away from the goal is a waste

There were a couple of things that I expected to result in significant improvements, but in testing either had negligible or negative impacts, and so aren't part of the final algorithm:

-   Favoring protected checkers
-   Trying to account for the risk of getting trapped
-   Valuing checkers closer to the goal non-linearly (ie. a checker right next to the goal is _way_ more valuable than one right next to home)
-   Optimizing for the number of legal moves

### Performance

I spent a substantial amount of time optimizing the performance of this solution. Running a profiler against a tournament led me to introduce significant memoization (using Python's excellent [`functools.cache`/`functools.cached_property`][caching]) throughout the system, and to optimize the equality checking and hashing of various classes. This ultimately resulted in a 2-3x performance increase over the initial version.

[caching]: https://docs.python.org/3/library/functools.html

## Running the Code

There are a number of ways to run the code directly, in addition to the examples provided in the report ([Jupyter Notebook](src/report.ipynb), [PDF](report.pdf)).

First, much of the code, especially the game foundation, is unit tested through Python's [doctest][] module. Tests can be run from the command line:

```bash
# This prints nothing if the tests pass
$ python3 -m doctest src/*.py
```

Additionally, I built a simple CLI for interacting with the game system:

```bash
$ python3 src/cli.py --help
usage: cli.py [-h] [-n ROUNDS] [-b BOARD_SIZE] [-c CHECKERS] [-d DIE_SIZE] [-s SEED]
              {g,game,t,tournament,r,roundrobin} {first,human,knowledge,last,random,score} [{first,human,knowledge,last,random,score} ...]

positional arguments:
  {g,game,t,tournament,r,roundrobin}
                        game mode
  {first,human,knowledge,last,random,score}
                        player algorithms (2 for game our tournament, 2+ for round robin)

optional arguments:
  -h, --help            show this help message and exit
  -n ROUNDS, --rounds ROUNDS
                        number of matches to run
  -b BOARD_SIZE, --board-size BOARD_SIZE
                        board size
  -c CHECKERS, --checkers CHECKERS
                        checkers per player
  -d DIE_SIZE, --die-size DIE_SIZE
                        die size
  -s SEED, --seed SEED  the seed for the random roll generator

$ python3 src/cli.py game random human  # play against a random player
<Output not shown because it requires human input>

$ python3 src/cli.py tournament random first last score -n 3000  # run a tournament and show the aggregate results
Playing a Nannon{6,3,6} bulk tournament of 3000 games each between random, first, last, score. seed = 1618284126
Played 6 tournaments of 3000 games each. Took 3s.
Loser → | first   | last    | random  | score
-----------------------------------------------
random  | 53.5%   | 45.8%   | -       | 46.8%
first   | -       | 44.9%   | 46.5%   | 43.0%
last    | 55.1%   | -       | 54.2%   | 50.2%
score   | 57.0%   | 49.8%   | 53.2%   | -

$ python3 src/cli.py tournament last score first --seed 12345  # set the seed to any integer for consistent dice (doesn't affect the random player's decisions). We'll use the same seed as above
Playing a Nannon{6,3,6} bulk tournament of 100 games each between last, score, first. seed = 12345
Played 3 tournaments of 100 games each. Took 0s.
Loser → | first   | last    | score
-------------------------------------
last    | 55.0%   | -       | 48.0%
score   | 52.0%   | 52.0%   | -
first   | -       | 45.0%   | 48.0%
```

[doctest]: https://docs.python.org/3/library/doctest.html
