from typing import *

from players import *
from Dicestream import *
from main import Board, Turn, GameConfiguration


def play_game(black_player, white_player, dicestream: Dicestream = None, rolls: List[int] = None, seed: int = None,
               config: GameConfiguration = GameConfiguration(), silent=False) -> Player:
    if not silent:
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
            if not silent:
                print(f"{turn.player.long_str} rolled {roll}, but couldn't make any moves! SKIPPED!")
            turn = Turn(turn.board, player=turn.player.swapped, dicestream=turn.dicestream)
            continue
            
        if turn.player == Player.BLACK:
            turn = turn.make(black_player(legal_moves, roll))
        else:
            turn = turn.make(white_player(legal_moves, roll))
    
    if not silent:
        print(f"Winner: {turn.board.whowon.long_str} ({(black_player if turn.board.whowon == Player.BLACK else white_player).__name__})! ")
    
    return turn.board.whowon
    
    
if __name__ == '__main__':
    play_game(human_player, verbose_random_player)
