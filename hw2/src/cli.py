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
    from play_game import play_game
    from play_tournament import play_tournament
    from bulk_tournament import bulk_tournament
    from roundrobin import roundrobin
    from structs import GameConfiguration
    parser = argparse.ArgumentParser()

    parser.add_argument("mode", choices=['g', 'game', 't', 'tournament', 'r', 'roundrobin'], help="game mode")
    parser.add_argument("players", choices=[a.name for a in PlayerAlgorithm.all()],  nargs='+', help="player algorithms (2 for game our tournament, 2+ for round robin)")
    parser.add_argument("-n", "--rounds", help="number of matches to run", type=int, default=100)
    parser.add_argument('-b', '--board-size', help="board size", type=int, default=6)
    parser.add_argument('-c', '--checkers', help="checkers per player", type=int, default=3)
    parser.add_argument('-d', '--die-size', help='die size', type=int, default=6)
    parser.add_argument('-s', '--seed', type=int, default=None, help="the seed for the random roll generator")

    args = parser.parse_args()

    players = [PlayerAlgorithm.get(name.lower().strip()) for name in args.players]

    assert len(players) >= 2, "must provide at least two players!"

    config = GameConfiguration(args.board_size, args.checkers, args.die_size)

    if args.mode in ['g', 'game']:
        play_game(players[0], players[1], seed=args.seed, config=config)
    elif args.mode in ['t', 'tournament']:
        # Play tournament has better UI if we're only doing two players
        if len(players) == 2:
            play_tournament(players[0], players[1], rounds=args.rounds, seed=args.seed, config=config)
        else:
            bulk_tournament(players, rounds=args.rounds, seed=args.seed, config=config)
    elif args.mode in ['r', 'roundrobin']:
        roundrobin(players, seed=args.seed, config=config)


if __name__ == '__main__':
    main()
