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
    
    # def __new__(cls, board_size, checkers_per_player, die_size):
    #     assert checkers_per_player < die_size, "checkers per player must be less than die size to avoid stalemates"
    #     return super(cls, GameConfiguration).__new__(GameConfiguration, (board_size, checkers_per_player, die_size))

    def __str__(self):
        return f"{{{self.board_size},{self.checkers_per_player},{self.die_size}}}"


class BoardDescription(NamedTuple):
    """
    A named tuple allowing for simple description of the state of a board. All three attributes are
    strings containing only any number of `B` (for a black checker), `W` (for a white checker),
    or `-` (for no checker, valid for the board only). `home` and `goal` are order-independent,
    and the number of each character represents the number of that player's checkers that are in the
    relevant zone. The board is a string of length board_size, where each position represents the
    checker (or lack thereof) at the relevant position. The perspective player's home (which is not
    tracked by this class) is always at the left.
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


def swap_checkers(checkers: Iterable[Checker], config: GameConfiguration) -> List[Checker]:
    """
    Swap a list of checkers from one player's perspective to the other:

    >>> print_each(swap_checkers([Checker(Player.BLACK, 2), Checker(Player.WHITE, 1), Checker(Player.BLACK, 'HOME')], GameConfiguration()))
    Checker(B @ 3)
    Checker(B @ HOME)
    Checker(W @ 4)
    """
    return [Checker(
        checker.player,
        config.board_size - 1 - checker.position if checker.position.is_concrete else checker.position
    ) for checker in checkers]


@dataclass(frozen=True)
class Move:
    """
    A data class representing a move that can be made from a given turn. `checker` is a member of `turn.checker` (which,
    since Checkers are immutable, means it hasn't moved yet), and `to` is defined relative to `turn` (including the
    perspective.)

    NOTE: Since Moves, Turns, Checkers, and Positions are all immutable, this class represents a possible but
    not-yet-executed move. To execute the move, call Move#make (which returns a new Turn).
    """
    board: 'Board'
    checker: Checker
    to: Checker.Position
    
    def __str__(self):
        return f"Move({self.checker.player.short_str}: {self.checker.position.name} -> {self.to.name})"
    
    @property
    def player(self) -> Player:
        return self.checker.player

    @classmethod
    def create(cls, from_idx: Checker.Position.Value, to_idx: Checker.Position.Value, board: 'Board'):
        """
        Convenient way to create a Move.
        """
        from_idx = Checker.Position(from_idx)
        to_idx = Checker.Position(to_idx)
        checker = only(checker for checker in board.checkers if checker.position == from_idx)
        return Move(board, checker, to_idx)

    def draw(self, perspective: Player = None) -> str:
        board = self.executed
        checker = self.checker
        if perspective is not None:
            board = board.from_perspective(perspective)
            checker = checker if not checker.position.is_concrete or self.board.perspective == perspective else Checker(checker.player, self.board.config.board_size - 1 - checker.position)
        return board.draw([checker])

    @property
    def executed(self) -> 'Board':
        """
        Return the resulting board after this move has been executed.
        
        >>> print(Move.create(3, 4, Board(perspective=Player.BLACK, board=('', 'BWWBWB', ''))).executed)
        Board{6,3,6}(B: W [BWW-BB] -)
        >>> print(Move.create(5, 'GOAL', Board(perspective=Player.WHITE, board=('', 'BWWBWB', ''))).executed)
        Board{6,3,6}(W: - [BWWBW-] B)
        >>> print(Move.create(4, 'GOAL', Board(perspective=Player.WHITE, board=('', 'BWWBW-', 'B'))).executed)
        Board{6,3,6}(W: - [BWWB--] BW)
        """
        # Remove the checker that needs to be moved, and handle any captures
        new_checkers = []
        has_removed_target = False
        for checker in self.board.checkers:
            # Remove the checker to be moved, and we'll add it back later
            if checker == self.checker and not has_removed_target:
                has_removed_target = True
                continue
            elif self.to.is_concrete and checker.position == self.to:
                new_checkers += [Checker(checker.player, Checker.Position('HOME'))]
            else:
                new_checkers += [checker]
        
        # Add the newly-moved checker
        new_checkers += [Checker(self.checker.player, self.to)]
        
        return Board(perspective=self.board.perspective, checkers=new_checkers, config=self.board.config)


class Board:
    """
    A dataclass representing a turn of the game. Completely immutable.

    Any given turn can be seen from either player's perspective, irrespective of if it is that
    player's turn.
    """
    
    perspective: Player
    """ From who's perspective are we looking at the board? """
    
    checkers: List[Checker]
    """ All checker is play. Always a list of length 2 * checkers_per_player """
    
    config: GameConfiguration
    """ The configuration representing the variant of Nannon we're playing. """
    
    def __init__(self, board: Union[BoardDescription, Tuple[str, str, str]] = None, checkers: list[Checker] = None,
                 perspective: Player = Player.BLACK, config: GameConfiguration = GameConfiguration()):
        """
        >>> print(Board(('BW', 'B----W', 'WB')))
        Board{6,3,6}(B: BW [B----W] BW)
        >>> print(Board(('', 'BWBWBW', '')))
        Board{6,3,6}(B: - [BWBWBW] -)
        >>> print(Board(('', 'BWB--WBW', ''), config=GameConfiguration(8, 3, 6)))
        Board{8,3,6}(B: - [BWB--WBW] -)
        """
        assert board is None or checkers is None, "can only provide board OR checkers, not both!"
        
        if board:
            if isinstance(board, tuple) and not isinstance(board, BoardDescription) and len(board) == 3:
                board = BoardDescription(board[0], board[1], board[2])
            checkers = board.checkers

        assert len(checkers) == config.checkers_per_player * 2, f"incorrect number of checkers! (Expected {config.checkers_per_player * 2}, Got {len(checkers)})"
        
        # Sanity Checks
        assert is_unique([checker.position for checker in checkers if checker.position.is_concrete]), \
            "two checkers on the same spot!"
        
        self.perspective = perspective
        self.checkers = sorted(checkers)
        self.config = config
    
    def draw(self, ghost_checkers: List[Checker] = []) -> str:
        """
        Return a string with a human-readable view of the board.
        
        If ghost_checkers is provided, those checkers will be rendered greyed-out.

        >>> print(Board(perspective=Player.BLACK, board=('BBBWWW', '-B--W-', 'BW'), config=GameConfiguration(6, 5, 6)).draw())
                     Black →
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |     ○        ●     |
        Home → ○○○   |  ▲  ▲  ▲  ▲  ▲  ▲  |   ●●● ← Home
                                    ← White
        >>> print(Board(perspective=Player.BLACK, board=('BBBBBWWWWW', '------', ''), config=GameConfiguration(6, 5, 6)).draw())
                     Black →
        Goal →       |  ▼  ▼  ▼  ▼  ▼  ▼  |       ← Goal
                     |                    |
        Home → ○○○○○ |  ▲  ▲  ▲  ▲  ▲  ▲  | ●●●●● ← Home
                                    ← White
        >>> print(Board(perspective=Player.BLACK, board=('', '------', 'BBBBBWWWWW'), config=GameConfiguration(6, 5, 6)).draw())
                     Black →
        Goal → ●●●●● |  ▼  ▼  ▼  ▼  ▼  ▼  | ○○○○○ ← Goal
                     |                    |
        Home →       |  ▲  ▲  ▲  ▲  ▲  ▲  |       ← Home
                                    ← White
        >>> print(Board(perspective=Player.BLACK, board=('BW', 'WBWBWB', 'BW'), config=GameConfiguration(6, 5, 6)).draw())
                     Black →
        Goal → ●     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ○ ← Goal
                     |  ●  ○  ●  ○  ●  ○  |
        Home → ○     |  ▲  ▲  ▲  ▲  ▲  ▲  |     ● ← Home
                                    ← White

        >>> print(Board(perspective=Player.WHITE, board=('BW', 'WBWBWB', 'BW'), config=GameConfiguration(6, 5, 6)).draw())
                     White →
        Goal → ○     |  ▼  ▼  ▼  ▼  ▼  ▼  |     ● ← Goal
                     |  ●  ○  ●  ○  ●  ○  |
        Home → ●     |  ▲  ▲  ▲  ▲  ▲  ▲  |     ○ ← Home
                                    ← Black
        """
        # Checkers are represented by tuples of the form (is_ghost, Checker)
        checkers = [(True, checker) for checker in ghost_checkers] + [(False, checker) for checker in self.checkers]
        home = [checker for checker in checkers if checker[1].position == Checker.Position('HOME')]
        goal = [checker for checker in checkers if checker[1].position == Checker.Position('GOAL')]
        board = [None] * self.config.board_size  # type: List[Optional[Tuple[bool, Checker]]]

        for checker in checkers:
            if checker[1].position.is_concrete:
                board[checker[1].position] = checker
        
        def render(checker: Optional[Tuple[bool, Checker]]) -> str:
            if checker is None:
                return ' '
            elif checker[0]:  # if ghost checker
                return '-'  # f"\u001b[38;5;241m{checker[1].display_symbol}\u001b[0m"
            else:
                return checker[1].display_symbol

        board_checkers = '|  ' + '  '.join(render(checker) for checker in board) + '  |'
        
        board_top = '| ' + ' ▼ ' * self.config.board_size + ' |'
        board_bottom = '| ' + ' ▲ ' * self.config.board_size + ' |'
        
        # NOTE: left_top/left_bottom and right_top/right_bottom are the same length
        left_top = 'Goal → ' + ''.join([render(checker) for checker in goal if
                                        checker[1].player != self.perspective]).ljust(
            self.config.checkers_per_player, ' ') + ' '
        right_top = ' ' + ''.join([render(checker) for checker in goal if
                                   checker[1].player == self.perspective]).rjust(
            self.config.checkers_per_player, ' ') + ' ← Goal'
        
        left_bottom = 'Home → ' + ''.join([render(checker) for checker in home if
                                           checker[1].player == self.perspective]).ljust(
            self.config.checkers_per_player, ' ') + ' '
        right_bottom = ' ' + ''.join([render(checker) for checker in home if
                                      checker[1].player != self.perspective]).rjust(
            self.config.checkers_per_player, ' ') + ' ← Home'
        
        top_line = left_top + board_top + right_top
        bottom_line = left_bottom + board_bottom + right_bottom
        
        line_len = len(bottom_line)
        
        mid_line = ((' ' * len(left_bottom)) + board_checkers)
        
        return "\n".join([
            (' ' * len(left_top)) + self.perspective.long_str + ' →',
            top_line,
            mid_line,
            bottom_line,
            ('← ' + self.perspective.swapped.long_str).rjust(line_len - len(right_bottom), ' ')
        ])
    
    def print(self):
        """
        Print the output of draw()
        """
        print(self.draw())
    
    def __str__(self):
        home, board, goal = BoardDescription.from_checkers(self.checkers, config=self.config)
        
        return f"Board{self.config}({self.perspective.short_str}: {home or '-'} [{board}] {goal or '-'})"
    
    def __eq__(self, other: 'Board'):
        return self.perspective == other.perspective and self.config == other.config and self.checkers == other.checkers
    
    def __hash__(self):
        return hash((self.perspective, self.config, tuple(self.checkers)))
    
    @property
    def swapped(self):
        """
        Return the same game, but from the other player's perspective. This allows most logic to only be written for one
        player.

        >>> print(Board(perspective=Player.BLACK, board=('BW', '-B--W-', 'BW')).swapped)
        Board{6,3,6}(W: BW [-W--B-] BW)
        """
        return Board(
            perspective=self.perspective.swapped,
            checkers=swap_checkers(self.checkers, self.config),
            config=self.config
        )
    
    def from_perspective(self, perspective: Player):
        return self if self.perspective == perspective else self.swapped
    
    def is_winner(self, player: Player = None) -> bool:
        if player is None:
            player = self.perspective
        
        return all(
            checker.position == Checker.Position('GOAL') for checker in self.checkers if checker.player == player
        )

    @property
    def whowon(self) -> Optional[Player]:
        """
        Return the winner, or None if there is no winner.

        A player wins when they've gotten all their checkers off the board.

        >>> Board(perspective=Player.BLACK, board=('', '-----W', 'BBBWW')).whowon
        Player.BLACK
        >>> Board(perspective=Player.BLACK, board=('', '-----B', 'BBWWW')).whowon
        Player.WHITE
        >>> Board(perspective=Player.WHITE, board=('', '-----B', 'BBWWW')).whowon
        Player.WHITE
        >>> Board(perspective=Player.BLACK, board=('', '----WB', 'BBWW')).whowon is None
        True
        """
        if self.is_winner(Player.BLACK):
            return Player.BLACK
        elif self.is_winner(Player.WHITE):
            return Player.WHITE
        else:
            return None
    
    def is_open(self, position: Checker.Position, player: Player = None) -> bool:
        """
        Check if the perspective's player _could_ move a checker to the given position, if they had a suitable roll.
        
        NOTE: This method does not take into account if the player has the checker to move, nor if it's their turn.

        _Tested via open_positions._
        """
        if player is None:
            player = self.perspective
        
        if position == Checker.Position('GOAL'):  # The goal is always open
            return True
        elif position == Checker.Position('HOME'):  # The home is never open
            return False
        else:
            checkers_on_spot = [checker for checker in self.checkers if checker.position == position]
            if len(checkers_on_spot) == 0:
                return True
            # Definitely not free if we already have a checker there
            elif checkers_on_spot[0].player == player:
                return False
            # Otherwise, it's an opponent's checker so let's see if we can take it
            else:
                # Check for primes (two opponent pieces next to each other are protected)
                if position > 0:
                    maybe_protector = only(checker for checker in self.checkers if checker.position == position - 1)
                    if maybe_protector is not None and maybe_protector.player == player.swapped:
                        return False
                if position + 1 < self.config.board_size:
                    maybe_protector = only(checker for checker in self.checkers if checker.position == position + 1)
                    if maybe_protector is not None and maybe_protector.player == player.swapped:
                        return False
        return True
    
    @property
    def open_positions(self, player: Player = None) -> Iterator[Checker.Position]:
        """
        Return all the positions that the player (or the perspective's player) could move to, if they had the right roll.

        NOTE: This method does not take into account if the player has the checker to move, nor if it's their turn.

        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.BLACK, board=('BBBWWW', '------', '')).open_positions]))
        '0, 1, 2, 3, 4, 5, GOAL'
        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.BLACK, board=('BWWW',   '-B---B', '')).open_positions]))
        '0, 2, 3, 4, GOAL'
        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.BLACK, board=('BBB',    '--WW-W', '')).open_positions]))
        '0, 1, 4, 5, GOAL'

        And for white:
        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.WHITE, board=('BWW',    'BB---W', '')).open_positions]))
        '2, 3, 4, GOAL'
        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.WHITE, board=('WB',     'WW--BB', '')).open_positions]))
        '2, 3, GOAL'
        >>> ", ".join(sorted([p.name for p in Board(perspective=Player.WHITE, board=('B',      'WBW-WB', '')).open_positions]))
        '1, 3, 5, GOAL'
        """
        # The goal is always open
        yield Checker.Position('GOAL')
        
        # Check all the other spots
        for i in range(0, self.config.board_size):
            position = Checker.Position(i)
            if self.is_open(position, player):
                yield position

    def legal_moves(self, roll: int, player: Player = None) -> List[Move]:
        """
        Returns all legal moves for the player (or the perspective player) from the current state.

        >>> print_each(Board(('BBBWWW', '------', ''), perspective=Player.BLACK).legal_moves(3))
        Move(B: HOME -> 2)
        >>> print_each(Board(('', 'BWWBWB', ''), perspective=Player.BLACK).legal_moves(1))
        Move(B: 3 -> 4)
        Move(B: 5 -> GOAL)
        >>> print_each(Board(('', 'BWWBWB', ''), perspective=Player.WHITE).legal_moves(1, Player.WHITE))
        Move(W: 2 -> 3)
        Move(W: 4 -> 5)
        >>> print_each(Board(('WBBB', 'W---W-', ''), perspective=Player.WHITE).legal_moves(3))
        Move(W: 0 -> 3)
        Move(W: 4 -> GOAL)
        Move(W: HOME -> 2)
        >>> print_each(Board(('', 'BWWBWB', ''), perspective=Player.WHITE).legal_moves(1))
        Move(W: 2 -> 3)
        Move(W: 4 -> 5)
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
        
        if player is None:
            player = self.perspective
        
        moves = []  # type: List[Move]
    
        # All checkers at home are equivalent, so we want to only generate moves for one of them
        had_checker_at_home = False
    
        for checker in self.checkers:
            # We can't move our opponent's checkers
            if checker.player != player:
                continue
        
            # A checker in the goal never moves
            if checker.position == Checker.Position('GOAL'):
                continue
        
            if checker.position == Checker.Position('HOME'):
                if had_checker_at_home:
                    continue
                had_checker_at_home = True
        
            to_idx = roll + checker.position
        
            if to_idx < self.config.board_size:
                to_pos = Checker.Position(to_idx)
            else:
                to_pos = Checker.Position('GOAL')
        
            if self.is_open(to_pos):
                moves += [Move(self, checker, to_pos)]
        
        return moves

    def score(self, player: Player = None):
        """
        Return player's score, which is the sum of the position of all the checkers (where home is 0pts, the board is
        1...board_size pts, and the goal is board_size + 1 pts).
        """
        if player is None:
            player = self.perspective

        if player != self.perspective:
            return self.swapped.score(player)

        total = 0
        for checker in self.checkers:
            if checker.player != player:
                continue

            if checker.position == Checker.Position('HOME'):
                # Home is 0 points
                continue
            elif checker.position == Checker.Position('GOAL'):
                total += self.config.board_size + 1
            else:
                total += checker.position + 1

        return total

    @classmethod
    def create_starting_board(cls, config: GameConfiguration = GameConfiguration(), perspective: Player = Player.BLACK):
        """
        Create a starting board for config.

        >>> print(Board.create_starting_board())
        Board{6,3,6}(B: BW [BB--WW] -)
        >>> print(Board.create_starting_board(GameConfiguration(6, 3, 6)))
        Board{6,3,6}(B: BW [BB--WW] -)
        >>> print(Board.create_starting_board(GameConfiguration(7, 4, 6)))
        Board{7,4,6}(B: BBWW [BB---WW] -)
        >>> print(Board.create_starting_board(GameConfiguration(8, 3, 6), Player.WHITE))
        Board{8,3,6}(W: BW [WW----BB] -)
        >>> print(Board.create_starting_board(GameConfiguration(8, 4, 6), Player.WHITE))
        Board{8,4,6}(W: BW [WWW--BBB] -)
        """
        # TODO: the spec is unclear as to the starting configuration for size > 6
        checkers_start_on_board = min(config.checkers_per_player - 1, (config.board_size // 2) - 1)
        checkers_at_home = config.checkers_per_player - checkers_start_on_board
        
        checkers = [
                       Checker(perspective, Checker.Position('HOME')),
                       Checker(perspective.swapped, Checker.Position('HOME'))
                   ] * checkers_at_home
        
        for i in range(0, checkers_start_on_board):
            checkers += [
                Checker(perspective, Checker.Position(i)),
                Checker(perspective.swapped, Checker.Position(config.board_size - 1 - i))
            ]
            
        # Sanity Check
        assert len(checkers) == 2 * config.checkers_per_player, "wrong number of checkers!"
        
        return cls(checkers=checkers, perspective=perspective, config=config)


class Turn:
    """
    A dataclass representing a turn of the game. Completely immutable.

    Any given turn can be seen from either player's perspective, irrespective of if it is that
    player's turn.
    """
    board: Board
    """ The current board. """
    
    player: Player
    """ Who's turn is it? """
    
    dicestream: Dicestream
    """
    The dicestream we're using. Importantly, this is only touched once at creation time when this
    turn's roll is calculated.
    """
    
    def __init__(self, board: Board, player: Player = Player.BLACK,
        dicestream: Dicestream = None, seed: int = None, rolls: List[int] = None):
        """
        >>> print(Turn(Board(('BW', 'B----W', 'WB')), seed=1))
        <Turn(B): Board{6,3,6}(B: BW [B----W] BW)>
        >>> print(Turn(Board(('', 'BWBWBW', '')), seed=1))
        <Turn(B): Board{6,3,6}(B: - [BWBWBW] -)>
        >>> print(Turn(Board(('', 'BWB--WBW', ''), config=GameConfiguration(8, 3, 6)), seed=1))
        <Turn(B): Board{8,3,6}(B: - [BWB--WBW] -)>
        """
        if dicestream is None:
            if rolls is not None:
                dicestream = Dicestream.fixed(rolls)
                assert seed is None, "seed cannot be provided if rolls is provided"
            else:
                dicestream = Dicestream.random(board.config.die_size, seed)
        else:
            assert seed is None, "seed cannot be provided if dicestream is provided"
            assert rolls is None, "rolls cannot be provided if dicestream is provided"
        
        # Sanity Checks
        assert dicestream.die_size == board.config.die_size, "dicestream's die size must match game config's die_size!"
        # FIXME: assert config.die_size >= abs(roll) >= 1, "roll must be in range [1, die_size]"
        assert \
            is_unique(checker.position for checker in board.checkers if checker.position.is_concrete), \
            "two checkers on the same spot!"
        
        if board.perspective != player:
            board = board.swapped

        self.board = board
        self.player = player
        self.dicestream = dicestream
        
    def __str__(self):
        return f"<Turn({self.player.short_str}): {str(self.board)}>"
    
    def __eq__(self, other: 'Turn'):
        # FIXME: Ignores dicestream
        return self.board == other.board and self.player == other.player
    
    def __hash__(self):
        return hash((self.board, self.player))
    
    @property
    def is_winner(self) -> bool:
        return self.board.is_winner(self.player)
    
    def make(self, move: Move) -> 'Turn':
        """
        Make a move and return the resulting turn.
        """
        assert move.board == self.board, "cannot make a move not for this board!"
        assert move.player == self.player, "cannot make a move out of turn!"
        return Turn(move.executed, player=self.player.swapped, dicestream=self.dicestream)


def start_game(dicestream: Dicestream = None, rolls: List[int] = None, seed: int = None,
               config: GameConfiguration = GameConfiguration(), perspective: Player = Player.BLACK):
    """
    Create a starting game state.

    >>> print(start_game(rolls=[1, 2, 3]))
    <Turn(W): Board{6,3,6}(W: BW [WW--BB] -)>
    >>> print(start_game(rolls=[1, 2, 3], config=GameConfiguration(6, 3, 6)))
    <Turn(W): Board{6,3,6}(W: BW [WW--BB] -)>
    >>> print(start_game(seed=1, config=GameConfiguration(7, 4, 6)))
    <Turn(W): Board{7,4,6}(W: BBWW [WW---BB] -)>
    >>> print(start_game(Dicestream.fixed([1, 2]), perspective=Player.WHITE, config=GameConfiguration(8, 3, 6)))
    <Turn(W): Board{8,3,6}(W: BW [BB----WW] -)>
    >>> print(start_game(Dicestream.fixed([1, 2]), perspective=Player.WHITE, config=GameConfiguration(8, 4, 6)))
    <Turn(W): Board{8,4,6}(W: BW [BBB--WWW] -)>
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
    
    initial_state = Turn(board=Board(('BW' * checkers_at_home, board, ''), config=config, perspective=perspective),
                        player=starting_player, dicestream=dicestream)
    
    return initial_state


if __name__ == "__main__":
    import doctest
    
    # Run all the unit tests
    failures, tests = doctest.testmod()
    if failures == 0 and tests > 0:
        print("Tests Passed!")
