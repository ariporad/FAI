#!/usr/bin/env python3
"""
A simple CLI wrapper for easily running tournaments.
"""
import argparse

from main import GameConfiguration
from Dicestream import Dicestream
from players import PLAYERS
from play_game import play_game
from play_tournament import play_tournament


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("player1", choices=PLAYERS.keys(), help="player 1 algorithm")
    parser.add_argument("player2", choices=PLAYERS.keys(), help="player 2 algorithm")
    parser.add_argument("-n", "--n-pairs", help="number of matches to run", type=int, default=0)
    parser.add_argument('-b', '--board-size', help="board size", type=int, default=6)
    parser.add_argument('-c', '--checkers', help="checkers per player", type=int, default=3)
    parser.add_argument('-d', '--die-size', help='die size', type=int, default=6)
    dicestream_opts = parser.add_mutually_exclusive_group()
    dicestream_opts.add_argument('-r', '--rolls', action='append', type=int, help="pre-define the values that will be rolled")
    dicestream_opts.add_argument('-s', '--seed', type=int, default=None, help="specify the seed for the random roll generator")
    dicestream_opts.add_argument('-R', '--random', action='store_const', const=True, default=True, help="generate random rolls with an arbitrary seed (default)")
    
    args = parser.parse_args()
    
    player1 = PLAYERS[args.player1]
    player2 = PLAYERS[args.player2]
    
    config = GameConfiguration(args.board_size, args.checkers, args.die_size)
    
    if args.rolls is not None:
        dicestream = Dicestream.fixed(args.rolls, die_size=config.die_size)
    else:
        dicestream = Dicestream.random(seed=args.seed, die_size=config.die_size)
        
    if args.n_pairs == 0:
        play_game(player1, player2, dicestream=dicestream, config=config)
    else:
        play_tournament(player1, player2, args.n_pairs, dicestream, config)
        
        
if __name__ == '__main__':
    main()
