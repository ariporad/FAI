from typing import *

from helpers import *
from structs import GameConfiguration, Player
from Board import Board


def explore(config: GameConfiguration = GameConfiguration()):
    """
    Return all possible boards for a game of Nannon.
    
    No tests because they're too slow.
    """
    children = {}
    to_explore = []  # type: List[Board]
    all_boards = []  # type: List[Board]

    # We need to special case the first roll, which is where both players roll a die and the player who rolled the
    # highest gets the difference (in a tie, they re-roll).
    initial_board = Board.create_starting_board(config, perspective=Player.BLACK)
    children[initial_board] = []
    # For the first roll, the highest you can roll is die_size - 1 (because it's the difference and the other player
    # has to roll at least 1).
    for roll in range(1, config.die_size):
        children[initial_board] += [move.executed for move in initial_board.legal_moves(roll)]
        children[initial_board] += [move.executed.from_perspective(Player.BLACK) for move in initial_board.swapped.legal_moves(roll)]

    # Ensure we only store unique children
    children[initial_board] = list(set(children[initial_board]))
    all_boards += [initial_board]
    to_explore += children[initial_board]

    # Now explore every other board
    for board in to_explore:  # this will continue iterating on states that we add inside the loop
        if board not in children:  # only explore new states
            children[board] = []
            for roll in range(1, config.die_size + 1):
                # make sure to check both perspectives
                children[board] += [move.executed for move in board.legal_moves(roll)]
                children[board] += [move.executed.from_perspective(Player.BLACK) for move in board.swapped.legal_moves(roll)]
            all_boards += [board]
            to_explore += children[board]

    return all_boards
