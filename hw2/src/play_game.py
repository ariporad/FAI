from typing import *
from random import choice

from Player import *
from helpers import *
from Dicestream import *
from main import Move, Board, Turn, GameConfiguration


def play_game(black_player, white_player, dicestream: Dicestream = None, rolls: List[int] = None, seed: int = None,
               config: GameConfiguration = GameConfiguration(), interactive=True):
    print(f"Playing a Game of Nannon{config}! Black: {black_player.__name__}, White: {white_player.__name__}")
    
    if dicestream is None:
        if rolls is not None:
            dicestream = Dicestream.fixed(rolls)
            assert seed is None, "seed cannot be provided if rolls is provided"
        else:
            dicestream = Dicestream.random(config.die_size, seed)
    else:
        assert seed is None, "seed cannot be provided if dicestream is provided"
        assert rolls is None, "rolls cannot be provided if dicestream is provided"
    
    starting_roll = dicestream.first_roll()
    starting_player = Player.BLACK
    if starting_roll < 0:
        starting_roll *= -1
        starting_player = Player.WHITE
        
    turn = Turn(Board.create_starting_board(config, starting_player), player=starting_player, dicestream=dicestream)
    
    while turn.board.whowon is None:
        roll = dicestream.roll() # FIXME: didn't take first roll into account!
        legal_moves = turn.board.legal_moves(roll)
        
        if len(legal_moves) == 0:
            print(f"{turn.player.long_str} rolled {roll}, but couldn't make any moves! SKIPPED!")
            turn = Turn(turn.board, player=turn.player.swapped, dicestream=turn.dicestream)
            continue
            
        if turn.player == Player.BLACK:
            turn = turn.make(black_player(legal_moves, roll))
        else:
            turn = turn.make(white_player(legal_moves, roll))
    
    print(f"Winner: {turn.board.whowon.long_str} ({(black_player if turn.board.whowon == Player.BLACK else white_player).__name__})! ")
    
    
def human_player(moves: List[Move], roll: int) -> Move:
    """
    A Nannon player that prompts the user to select a move.
    """
    
    print(f"Your Turn (You Rolled {roll}):")
    print(join_horizontal((move.draw(Player.BLACK) for move in moves), '\t'))
    
    choice = int(input(f"Select an Option (1-{len(moves)}):"))
    if not (1 <= choice <= len(moves)):
        print("Invalid Selection!")
        return human_player(moves, roll)
    
    return moves[choice - 1]
    
    
def random_player(moves: List[Move], roll: int) -> Move:
    """
    A Nannon player that picks a move at random.
    """
    return choice(moves)


def make_player_verbose(player, name: str = "Player"):
    """
    Wrap a player to make it print every move it makes.
    """
    def new_player(moves: List[Move], roll: int) -> Move:
        print(f"{name} (Rolled {roll}) Picked:")
        move = player(moves, roll)
        print(move.draw(Player.BLACK))
        return move

    new_player.__name__ = player.__name__
    
    return new_player




if __name__ == '__main__':
    play_game(human_player, make_player_verbose(random_player, 'Random Player'))
