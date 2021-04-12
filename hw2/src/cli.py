#!/usr/bin/env python3
"""
A simple CLI wrapper for easily running tournaments.
"""


def main():
    # These imports need to be inside this function because, if they don't, the Player enum literally gets black and
    # white confused (ie. `Player.BLACK.long_str == "White"`), but only when running all of the doctests from PyCharm.
    # This is even true given that no actual code from this file runs in a testing environment--just the imports alone
    # cause the issue. Re-ordering the imports has no effect. The issue persists across reboots. Not including this file
    # in the doctest target, or running the tests from the command line, or putting the imports inside this function
    # (which doesn't run in a testing environment) resolves the situation. As best I can tell, there are no other
    # effects of any kind.
    #
    # Careful observers will note that this file neither imports nor touches Player. It isn't imported by anything, so
    # it can't create a circular dependency. For that matter, Player.py doesn't import anything (except the standard
    # library), so it can *never* be the subject of a circular dependency problem. And even so, the issue isn't that
    # Player isn't defined, or that it doesn't have the right value--it's that methods of Player seem to get confused
    # about what instance they're being called on.
    #
    # I wish this was a joke.

    import argparse

    from players import PlayerAlgorithm
    from Dicestream import Dicestream
    from play_game import play_game
    from play_tournament import play_tournament
    from main import GameConfiguration
    parser = argparse.ArgumentParser()

    parser.add_argument("player1", choices=[a.name for a in PlayerAlgorithm.all()], help="player 1 algorithm")
    parser.add_argument("player2", choices=[a.name for a in PlayerAlgorithm.all()], help="player 2 algorithm")
    parser.add_argument("-n", "--n-pairs", help="number of matches to run", type=int, default=0)
    parser.add_argument('-b', '--board-size', help="board size", type=int, default=6)
    parser.add_argument('-c', '--checkers', help="checkers per player", type=int, default=3)
    parser.add_argument('-d', '--die-size', help='die size', type=int, default=6)
    parser.add_argument('-s', '--seed', type=int, default=None, help="the seed for the random roll generator")

    args = parser.parse_args()

    player1 = PlayerAlgorithm.get(args.player1.lower().strip())
    player2 = PlayerAlgorithm.get(args.player2.lower().strip())

    config = GameConfiguration(args.board_size, args.checkers, args.die_size)

    if args.n_pairs == 0:
        play_game(player1, player2, seed=args.seed, config=config)
    else:
        play_tournament(player1, player2, args.n_pairs, args.seed, config)


if __name__ == '__main__':
    main()
