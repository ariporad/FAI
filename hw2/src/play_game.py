from typing import *
from players import *
from Dicestream import *
from main import Board, Turn, GameConfiguration


def play_game(black_player: PlayerAlgorithm, white_player: PlayerAlgorithm,
              dicestream: Dicestream = None, rolls: List[int] = None, seed: int = None,
              config: GameConfiguration = GameConfiguration(), silent=False) -> Player:
    if dicestream is None:
        if rolls is not None:
            dicestream = Dicestream.fixed(rolls)
            assert seed is None, "seed cannot be provided if rolls is provided"
        else:
            if seed is None:
                seed = random_seed()
            dicestream = Dicestream.random(config.die_size, seed)
    else:
        assert seed is None, "seed cannot be provided if dicestream is provided"
        assert rolls is None, "rolls cannot be provided if dicestream is provided"

    if not silent:
        print(f"Playing a Game of Nannon{config}! Black: {black_player.name}, White: {white_player.name}. Seed = {seed}")

    starting_roll = dicestream.first_roll()
    starting_player = Player.BLACK
    if starting_roll < 0:
        starting_roll *= -1
        starting_player = Player.WHITE
        
    turn = Turn(Board.create_starting_board(config, starting_player), player=starting_player, dicestream=dicestream)

    is_first_turn = True
    while turn.board.whowon is None:
        roll = starting_roll if is_first_turn else dicestream.roll()
        player = black_player if turn.player == Player.BLACK else white_player
        assert turn.board.perspective == turn.player
        legal_moves = turn.board.legal_moves(roll)
        is_first_turn = False

        num_moves = len(legal_moves)
        if num_moves == 0:
            if not silent:
                print(f"{turn.player.long_str} ({player.name}) rolled {roll}, but couldn't make any moves! SKIPPED!")
            turn = Turn(turn.board, player=turn.player.swapped, dicestream=turn.dicestream)
            continue
        elif num_moves == 1:
            move = legal_moves[0]
        else:
            move = player.play(legal_moves, roll)

        if not silent and not player.force_silent:
            print(f"{turn.player.long_str} ({player.name}) rolled {roll} and played:")
            print(move.draw(Player.BLACK))

        turn = turn.make(move)

    if not silent:
        print(f"Winner: {turn.board.whowon.long_str} ({(black_player if turn.board.whowon == Player.BLACK else white_player).name})! ")
    
    return turn.board.whowon
    
    
if __name__ == '__main__':
    play_game(HumanPlayerAlgorithm(), RandomPlayerAlgorithm())
