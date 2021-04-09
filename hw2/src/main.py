#!/usr/bin/env python3
from collections import namedtuple

from Checker import *
from Dicestream import *
from helpers import *


# Question: a number of my functions don't have the same names as the ones perscribed. Is that OK?


class GameConfiguration(NamedTuple):
    """
    A named tuple representing the particular variant of Nannon we're playing. Completely immutable.

    The defaults represent standard Nannon, with a 6 positions on the board, 3 checkers per player,
    and a standard six-sided die.
    """
    
    board_size: int = 6
    checkers_per_player: int = 3
    die_size: int = 6
    
    def __str__(self):
        return f"{{{self.board_size},{self.checkers_per_player},{self.die_size}}}"


class BoardDescription(NamedTuple):
    """
    A named tuple allowing for simple description of the state of a board. All three attributes are
    strings containing only any number of `B` (for a black checker), `W` (for a white checker),
    or `-` (for no checker, valid for the board only). `home` and `goal` are order-independent,
    and the number of each character represents the number of that player's checkers that are in the
    relevant zone. The board is a string of length board_size, where each position represents the
    checker (or lack thereof) at the relevant position. Black's home is always at the left.
    """
    
    home: str
    board: str
    goal: str
    
    def __eq__(self, other):
        # Using numerical indexes to allow comparing against normal tuples
        return isinstance(other, tuple) and sorted(self[0]) == sorted(other[0]) and self[1] == other[1] and sorted(
            self[2]) == sorted(other[2])
    
    def __ne__(self, other):
        return not (self == other)
    
    @classmethod
    def from_checkers(cls, checkers: List[Checker], config: GameConfiguration = GameConfiguration()):
        """
        Convert from a list of Checkers to a BoardDescription.

        >>> board1 = BoardDescription('BW', '--W--B', 'WB')
        >>> BoardDescription.from_checkers(board1.checkers) == board1
        True
        >>> board2 = BoardDescription('', 'BWBWBW', '')
        >>> BoardDescription.from_checkers(board2.checkers) == board2
        True
        """
        home = ''.join(
            [checker.player.short_str for checker in checkers if checker.position == Checker.Position('HOME')])
        goal = ''.join(
            [checker.player.short_str for checker in checkers if checker.position == Checker.Position('GOAL')])
        
        board = ['-'] * config.board_size
        
        for checker in checkers:
            if not checker.position.is_concrete:
                continue
            
            board[checker.position] = checker.player.short_str
        
        return cls(home, ''.join(board), goal)
    
    @property
    def checkers(self) -> List[Checker]:
        """
        Convert this BoardDescription to a list of Checkers.
        >>> print_each(BoardDescription('BW', '--W--B', 'WB').checkers)
        Checker(B @ 5)
        Checker(B @ GOAL)
        Checker(B @ HOME)
        Checker(W @ 2)
        Checker(W @ GOAL)
        Checker(W @ HOME)
        >>> print_each(BoardDescription('', 'BWBWBW', '').checkers)
        Checker(B @ 0)
        Checker(B @ 2)
        Checker(B @ 4)
        Checker(W @ 1)
        Checker(W @ 3)
        Checker(W @ 5)
        """
        checkers = []  # type: List[Checker]
        
        checkers += [Checker(Player.BLACK, Checker.Position('HOME'))] * self.home.count('B')
        checkers += [Checker(Player.WHITE, Checker.Position('HOME'))] * self.home.count('W')
        
        checkers += [Checker(Player.BLACK, Checker.Position('GOAL'))] * self.goal.count('B')
        checkers += [Checker(Player.WHITE, Checker.Position('GOAL'))] * self.goal.count('W')
        
        for i in range(0, len(self.board)):
            if self.board[i] == 'B':
                checkers += [Checker(Player.BLACK, Checker.Position(i))]
            elif self.board[i] == 'W':
                checkers += [Checker(Player.WHITE, Checker.Position(i))]
        
        return checkers


@dataclass(frozen=True)
class Move:
    turn: 'Turn'
    checker: Checker
    to: Checker.Position
    
    def __str__(self):
        return f"Move({self.checker.player.short_str}: {self.checker.position.name} -> {self.to.name})"
    
    def make(self) -> 'Turn':
        """
        Execute this move and return a new Turn.
        
        >>> print(next(Turn(perspective=Player.BLACK, rolls=[3, 1], board=('', 'BWWBWB', '')).legal_moves).make())
        <Turn{6,3,6} B:W 1 - [BWW-WB] B>
        >>> print_each(Turn(perspective=Player.BLACK, roll=1, board=('', 'BWWBWB', '')).legal_moves)
        Move(B: 3 -> 4)
        Move(B: 5 -> GOAL)
        >>> print(next(Turn(perspective=Player.WHITE, player=Player.WHITE, rolls=[1, 1], board=('', 'BWWBWB', '')).legal_moves).make())
        <Turn{6,3,6} W:B 1 B [BWWW-W] ->
        >>> print_each(Turn(perspective=Player.WHITE, player=Player.WHITE, roll=3, board=('WBBB', '--W-W-', '')).legal_moves)
        Move(W: 1 -> 4)
        Move(W: 3 -> GOAL)
        Move(W: HOME -> 2)
        """
        # Remove the checker that needs to be moved, and handle any captures
        checkers = [
            Checker(checker.player, Checker.Position('HOME')) if checker.position == self.to else checker
            for checker in self.turn.checkers
            if checker != self.checker
        ]
        
        # Add the newly-moved checker
        checkers += [Checker(self.checker.player, self.to)]
        
        return Turn(perspective=self.turn.perspective, player=self.turn.player.swapped,
                    roll=self.turn.dicestream.roll(), checkers=checkers, config=self.turn.config,
                    dicestream=self.turn.dicestream)


class Turn:
    """
    A dataclass representing a turn of the game. Completely immutable.

    Any given turn can be seen from either player's perspective, irrespective of if it is that
    player's turn.
    """
    
    perspective: Player
    """ From who's perspective are we looking at the board? """
    
    player: Player
    """ Who's turn is it? """
    
    roll: Optional[int]
    """ Dice value that was rolled. If None, then the first turn hasn't been played yet. """
    
    checkers: List[Checker]
    """ All checker is play. Always a list of length 2 * checkers_per_player """
    
    config: GameConfiguration
    """ The configuration representing the variant of Nannon we're playing. """
    
    dicestream: Dicestream
    """
    The dicestream we're using. Importantly, this is only touched once at creation time when this
    turn's roll is calculated.
    """
    
    def __init__(self, board: Union[BoardDescription, Tuple[str, str, str]] = None, checkers: list[Checker] = None,
                 roll: int = None,
                 player: Player = Player.BLACK, perspective: Player = Player.BLACK,
                 config: GameConfiguration = GameConfiguration(),
                 dicestream: Dicestream = None, seed: int = None, rolls: List[int] = None):
        """
        >>> print(Turn(('BW', 'B----W', 'WB'), seed=1))
        <Turn{6,3,6} B:B 2 BW [B----W] BW>
        >>> print(Turn(('', 'BWBWBW', ''), seed=1))
        <Turn{6,3,6} B:B 2 - [BWBWBW] ->
        >>> print(Turn(('', 'BWB--WBW', ''), seed=1, config=GameConfiguration(8, 3, 6)))
        <Turn{8,3,6} B:B 2 - [BWB--WBW] ->
        """
        assert board is None or checkers is None, "can only provide board OR checkers, not both!"
        
        if board:
            if isinstance(board, tuple) and not isinstance(board, BoardDescription) and len(board) == 3:
                board = BoardDescription(board[0], board[1], board[2])
            checkers = board.checkers
            # Board descriptions are always black perspective, so we need to flip it if we're white
            if perspective != Player.BLACK:
                checkers = [Checker(checker.player, config.board_size - 1 - checker.position) for checker in checkers]
            
        assert len(checkers) == config.checkers_per_player * 2, "incorrect number of checkers!"
        
        if dicestream is None:
            if rolls is not None:
                dicestream = Dicestream.fixed(rolls)
                assert seed is None, "seed cannot be provided if rolls is provided"
            else:
                dicestream = Dicestream.random(config.die_size, seed)
        else:
            assert seed is None, "seed cannot be provided if dicestream is provided"
            assert rolls is None, "rolls cannot be provided if dicestream is provided"
        
        if roll is None:
            roll = dicestream.roll()
        
        # Sanity Checks
        assert config.checkers_per_player < config.die_size, "checkers per player must be less than die size to avoid stalemates"
        assert dicestream.die_size == config.die_size, "dicestream's die size must match game config's die_size!"
        assert config.die_size >= abs(roll) >= 1, "roll must be in range [1, die_size]"
        assert is_unique([checker.position for checker in checkers if
                          checker.position.is_concrete]), "two checkers on the same spot!"
        
        self.perspective = perspective
        self.player = player
        self.roll = roll
        self.checkers = checkers
        self.config = config
        self.dicestream = dicestream
    
    LinearCheckers = namedtuple('LinearCheckers', ['home', 'goal', 'board'])
    
    @property
    # TODO: this should be combined with BoardDescriptor
    def linear_checkers(self) -> 'LinearCheckers':
        home = []  # type: List[Checker]
        goal = []  # type: List[Checker]
        board = [None] * self.config.board_size  # type: List[Optional[Checker]]
        
        for checker in self.checkers:
            if checker.position == Checker.Position('HOME'):
                home.append(checker)
            elif checker.position == Checker.Position('GOAL'):
                goal.append(checker)
            else:
                board[checker.position] = checker
        
        return self.LinearCheckers(home=home, goal=goal, board=board)
    
    def print_board(self):
        """
        Print a human-readable view of the board.

        >>> Turn(perspective=Player.BLACK, player=Player.BLACK, roll=3, board=('BBBWWW', '-B--W-', 'BW'), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |     ○        ●     |
        Home → ○○○   |  ▲  ▲  ▲  ▲  ▲  ▲  |   ●●● ← Home
                                    ← White
        >>> Turn(perspective=Player.BLACK, player=Player.BLACK, roll=3, board=('BBBBBWWWWW', '------', ''), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →
        Goal →       |  ▼  ▼  ▼  ▼  ▼  ▼  |       ← Goal
                     |                    |
        Home → ○○○○○ |  ▲  ▲  ▲  ▲  ▲  ▲  | ●●●●● ← Home
                                    ← White
        >>> Turn(perspective=Player.BLACK, player=Player.BLACK, roll=3, board=('', '------', 'BBBBBWWWWW'), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →
        Goal → ●●●●● |  ▼  ▼  ▼  ▼  ▼  ▼  | ○○○○○ ← Goal
                     |                    |
        Home →       |  ▲  ▲  ▲  ▲  ▲  ▲  |       ← Home
                                    ← White
        >>> Turn(perspective=Player.BLACK, player=Player.BLACK, roll=3, board=('BW', 'WBWBWB', 'BW'), config=GameConfiguration(6, 5, 6)).print_board()
                     Black →
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |  ●  ○  ●  ○  ●  ○  |
        Home → ○     |  ▲  ▲  ▲  ▲  ▲  ▲  |     ● ← Home
                                    ← White

        >>> Turn(perspective=Player.WHITE, player=Player.BLACK, roll=3, board=('BW', 'WBWBWB', 'BW'), config=GameConfiguration(6, 5, 6)).print_board()
                     White →
        Goal → ○     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ● ← Goal
                     |  ○  ●  ○  ●  ○  ●  |
        Home → ●     |  ▲  ▲  ▲  ▲  ▲  ▲  |     ○ ← Home
                                    ← Black
        """
        (home, goal, board) = self.linear_checkers
        
        board_checkers = '|  ' + '  '.join(
            [checker.display_symbol if checker is not None else ' ' for checker in board]) + '  |'
        
        board_top = '| ' + ' ▼ ' * self.config.board_size + ' |'
        board_bottom = '| ' + ' ▲ ' * self.config.board_size + ' |'
        
        # NOTE: left_top/left_bottom and right_top/right_bottom are the same length
        left_top = 'Goal → ' + ''.join([checker.display_symbol for checker in goal if
                                        checker.player != self.perspective]).ljust(
            self.config.checkers_per_player, ' ') + ' '
        right_top = ' ' + ''.join([checker.display_symbol for checker in goal if
                                   checker.player == self.perspective]).rjust(
            self.config.checkers_per_player, ' ') + ' ← Goal'
        
        left_bottom = 'Home → ' + ''.join([checker.display_symbol for checker in home if
                                           checker.player == self.perspective]).ljust(
            self.config.checkers_per_player, ' ') + ' '
        right_bottom = ' ' + ''.join([checker.display_symbol for checker in home if
                                      checker.player != self.perspective]).rjust(
            self.config.checkers_per_player, ' ') + ' ← Home'
        
        top_line = left_top + board_top + right_top
        bottom_line = left_bottom + board_bottom + right_bottom
        
        line_len = len(bottom_line)
        
        mid_line = ((' ' * len(left_bottom)) + board_checkers)
        
        print(((' ' * len(left_top)) + self.perspective.long_str + ' →'))
        print(top_line)
        print(mid_line)
        print(bottom_line)
        print(
            ('← ' + self.perspective.swapped.long_str).rjust(line_len - len(right_bottom), ' '))
    
    def __str__(self):
        home, board, goal = BoardDescription.from_checkers(self.checkers, config=self.config)
        
        return f"<Turn{self.config} {self.perspective.short_str}:{self.player.short_str} {self.roll} {home or '-'} [{board}] {goal or '-'}>"
    
    @property
    def swapped(self):
        """
        Return the same game, but from the other player's perspective. This allows most logic to
        only be written for one player.

        >>> print(Turn(perspective=Player.BLACK, player=Player.BLACK, roll=3, board=('BW', '-B--W-', 'BW')).swapped)
        <Turn{6,3,6} W:B 3 BW [-B--W-] BW>
        """
        checkers = [Checker(checker.player, self.config.board_size - 1 - checker.position) for checker in self.checkers]
        return Turn(perspective=self.perspective.swapped, player=self.player, roll=self.roll, checkers=checkers,
                    config=self.config, dicestream=self.dicestream)
    
    @property
    def is_winner(self) -> bool:
        return all([
            checker.position == Checker.Position('GOAL') for checker in self.checkers if
            checker.player == self.perspective
        ])
    
    @property
    def whowon(self) -> Optional[Literal[-1, 1]]:
        """
        Return the winner (1 if it's us, -1 if it's not), or None if there is no winner.

        A player wins when they've gotten all their checkers off the board.

        >>> Turn(perspective=Player.BLACK, roll=3, board=('', '-----W', 'BBBWW')).whowon
        1
        >>> Turn(perspective=Player.BLACK, roll=3, board=('', '-----B', 'BBWWW')).whowon
        -1
        >>> Turn(perspective=Player.BLACK, roll=3, board=('', '----WB', 'BBWW')).whowon is None
        True
        >>> Turn(perspective=Player.WHITE, roll=3, board=('', '-----W', 'BBBWW')).whowon
        -1
        >>> Turn(perspective=Player.WHITE, roll=3, board=('', '-----B', 'BBWWW')).whowon
        1
        >>> Turn(perspective=Player.WHITE, roll=3, board=('', '----WB', 'BBWW')).whowon is None
        True
        """
        if self.is_winner:
            return 1
        elif self.swapped.is_winner:
            return -1
        else:
            return None
    
    def is_open(self, position: Checker.Position) -> bool:
        """
        Check if the perspective's player _could_ move a checker to the given position, if they had a suitable roll.
        
        NOTE: This method does not take into account if the player has the checker to move, nor if it's their turn.
        """
        
        if position == Checker.Position('GOAL'):  # The goal is always open
            return True
        elif position == Checker.Position('HOME'):  # The home is never open
            return False
        else:
            if self.linear_checkers.board[position] is None:  # Definitely open if spot is empty
                return True
            elif self.linear_checkers.board[position].player == self.perspective:  # Can't move where we have a Checker
                return False
            elif self.linear_checkers.board[position].player == self.perspective.swapped:
                # Check for primes (two opponent pieces next to each other are protected)
                if position > 0 and \
                    self.linear_checkers.board[position - 1] is not None and \
                    self.linear_checkers.board[position - 1].player == self.perspective.swapped:
                    return False
                elif position + 1 < len(self.linear_checkers.board) and \
                    self.linear_checkers.board[position + 1] is not None and \
                    self.linear_checkers.board[position + 1].player == self.perspective.swapped:
                    return False
                else:
                    return True
    
    @property
    def open_positions(self) -> Iterator[Checker.Position]:
        """
        Return all the positions that  the perspective's player _could_ move a checker to, if they had a suitable roll.

        NOTE: This method does not take into account if the player has the checker to move, nor if it's their turn.

        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.BLACK, roll=3, board=('BBBWWW', '------', '')).open_positions]))
        '0, 1, 2, 3, 4, 5, GOAL'
        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.BLACK, roll=3, board=('BWWW',   '-B---B', '')).open_positions]))
        '0, 2, 3, 4, GOAL'
        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.BLACK, roll=3, board=('BBB',    '--WW-W', '')).open_positions]))
        '0, 1, 4, 5, GOAL'

        And for white (remember that the positions returned are relative to white's side of the board, so they'll be
        inverted from black's side).
        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.WHITE, roll=3, board=('BWW',    'BB---W', '')).open_positions]))
        '1, 2, 3, GOAL'
        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.WHITE, roll=3, board=('WB',     'WW--BB', '')).open_positions]))
        '2, 3, GOAL'
        >>> ", ".join(sorted([p.name for p in Turn(perspective=Player.WHITE, roll=3, board=('B',      'WBW-WB', '')).open_positions]))
        '0, 2, 4, GOAL'
        """
        # The goal is always open
        yield Checker.Position('GOAL')
        
        # Check all the other spots
        for i in range(0, self.config.board_size):
            position = Checker.Position(i)
            if self.is_open(position):
                yield position
    
    @property
    def legal_moves(self) -> Iterator[Move]:
        """
        Returns all legal moves for the current player from the current state.
        
        NOTE: This method can only be called when the perspective player is the same as the current player.
        
        >>> print_each(Turn(perspective=Player.BLACK, roll=3, board=('BBBWWW', '------', '')).legal_moves)
        Move(B: HOME -> 2)
        >>> print_each(Turn(perspective=Player.BLACK, roll=1, board=('', 'BWWBWB', '')).legal_moves)
        Move(B: 3 -> 4)
        Move(B: 5 -> GOAL)
        >>> print_each(Turn(perspective=Player.WHITE, player=Player.WHITE, roll=1, board=('', 'BWWBWB', '')).legal_moves)
        Move(W: 1 -> 2)
        Move(W: 4 -> 5)
        >>> print_each(Turn(perspective=Player.WHITE, player=Player.WHITE, roll=3, board=('WBBB', '--W-W-', '')).legal_moves)
        Move(W: 1 -> 4)
        Move(W: 3 -> GOAL)
        Move(W: HOME -> 2)
        """
        # (LEGALMOVES POS ROLL) returns the position that player1 can move from with the current roll. This may be a
        # list of 0(nil), 1, 2 or 3 values indicating the board positions of player1's checkers. You might make a module
        # first which determines where player1 can land on the board (i.e. not on player 1 checkers or player 2 checkers
        # next to each other)
        #
        # Players start checkers at opposite ends of the board, take turns rolling one die, and, if possible, MUST move
        # one checker forward the number of steps given, or off the board. To determine who goes first, both players
        # roll their dice, and the winner gets the difference between the rolls (in case of tie, roll again). A checker
        # cannot legally land on another checker of the same color, nor on any of the opponent which are protected by an
        # adjacent checker on the board. Landing on a singleton opponent checker hits it back off the board.
        assert self.player == self.perspective, "only the current player has legal moves!"
        
        # All checkers at home are equivalent, so we want to only generate moves for one of them
        had_checker_at_home = False
        
        for checker in self.checkers:
            # We can't move our opponent's checkers
            if checker.player != self.perspective:
                continue
            
            # A checker in the goal never moves
            if checker.position == Checker.Position('GOAL'):
                continue
            
            if checker.position == Checker.Position('HOME'):
                if had_checker_at_home:
                    continue
                had_checker_at_home = True
            
            to_idx = self.roll + checker.position
            
            if to_idx < self.config.board_size:
                to_pos = Checker.Position(to_idx)
            else:
                to_pos = Checker.Position('GOAL')
            
            if self.is_open(to_pos):
                yield Move(self, checker, to_pos)


def start_game(dicestream: Dicestream = None, rolls: List[int] = None, seed: int = None,
               config: GameConfiguration = GameConfiguration(), perspective: Player = Player.BLACK):
    """
    Create a starting game state.

    >>> print(start_game(rolls=[1, 2, 3]))
    <Turn{6,3,6} B:W 1 BW [BB--WW] ->
    >>> print(start_game(rolls=[1, 2, 3], config=GameConfiguration(6, 3, 6)))
    <Turn{6,3,6} B:W 1 BW [BB--WW] ->
    >>> print(start_game(seed=1, config=GameConfiguration(7, 4, 6)))
    <Turn{7,4,6} B:W 3 BBWW [BB---WW] ->
    >>> print(start_game(Dicestream.fixed([1, 2]), perspective=Player.WHITE, config=GameConfiguration(8, 3, 6)))
    <Turn{8,3,6} W:W 1 BW [BB----WW] ->
    >>> print(start_game(Dicestream.fixed([1, 2]), perspective=Player.WHITE, config=GameConfiguration(8, 4, 6)))
    <Turn{8,4,6} W:W 1 BW [BBB--WWW] ->
    """
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
    
    # TODO: the spec is unclear as to the starting configuration for size > 6
    checkers_start_on_board = min(config.checkers_per_player - 1, (config.board_size // 2) - 1)
    blank_spaces = config.board_size - (checkers_start_on_board * 2)
    checkers_at_home = config.checkers_per_player - checkers_start_on_board
    
    # Black's home is always on the left
    board = ('B' * checkers_start_on_board) + ('-' * blank_spaces) + ('W' * checkers_start_on_board)
    
    initial_state = Turn(board=('BW' * checkers_at_home, board, ''), roll=starting_roll, player=starting_player,
                         perspective=perspective,
                         config=config, dicestream=dicestream)
    
    return initial_state


if __name__ == "__main__":
    import doctest
    
    # Run all the unit tests
    failures, tests = doctest.testmod()
    if failures == 0 and tests > 0:
        print("Tests Passed!")
