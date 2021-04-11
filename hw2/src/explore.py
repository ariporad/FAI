from typing import *

from main import Turn, Board, GameConfiguration
from Player import Player


def explore(config: GameConfiguration = GameConfiguration()):
    """
    >>> explore()
    """
    children = {}
    to_explore = []  # type: List[Turn]
    possible_states = []  # type: List[Turn]

    # We need to special case the first roll, which is where both players roll a die and the player who rolled the
    # highest gets the difference (in a tie, they re-roll). We represent this by creating two root states: one where
    # Black goes first (with a roll 1..die_size, exclusive), and one where White goes first (same roll options), then
    # expanding out from there.
    initial_board = Board.create_starting_board(config, perspective=Player.BLACK)
    root_turns = [Turn(initial_board, Player.BLACK, rolls=[]), Turn(initial_board, Player.WHITE, rolls=[])]
    for turn in root_turns:
        children[turn] = []
        # For the first roll, the highest you can roll is die_size - 1 (because it's the difference and the other player
        # has to roll at least 1).
        for roll in range(1, config.board_size):
            children[turn] += [turn.make(move) for move in turn.board.legal_moves(roll)]
        possible_states += [turn]
        to_explore += children[turn]
    
    for turn in to_explore:
        if turn not in children:
            children[turn] = []
            for roll in range(1, config.die_size + 1):
                children[turn] += [turn.make(move) for move in turn.board.legal_moves(roll)]
            possible_states += [turn]
            to_explore += children[turn]
    
    return possible_states
