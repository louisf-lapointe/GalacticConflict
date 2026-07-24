from pieces.piece import Piece
from game.move import Move, MoveTransform
from pieces.battleship import Battleship
import pygame


white_torpedo = pygame.image.load("pieces/assets/White_Torpedo.png")
black_torpedo = pygame.image.load("pieces/assets/Black_Torpedo.png")
Torpedo_images = [white_torpedo, black_torpedo]


white_torpedo_eval_table = [
    0,  0,  0,  5,  5,  0,  0,  0,
    0,  5, 10, 10, 10, 10,  5,  0,
    0,  5, 10, 15, 15, 10,  5,  0,
    0,  5, 10, 15, 15, 10,  5,  0,
    0,  5, 10, 15, 15, 10,  5,  0,
    0,  5, 10, 10, 10, 10,  5,  0,
    0,  5,  5,  5,  5,  5,  5,  0,
    0,  0,  0,  0,  0,  0,  0,  0
]

black_torpedo_eval_table = white_torpedo_eval_table[::-1]


class Torpedo(Piece):
    images = Torpedo_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []   # Torpedoes cannot be manually moved
        self.letter = "TP"

    # ---------------------------------------------------------
    # TORPEDO CANNOT BE SELECTED OR MOVED BY PLAYER
    # ---------------------------------------------------------
    def update_valid_moves(self, board):
        self.valid_moves = []
        return self.valid_moves

    # ---------------------------------------------------------
    # BEFORE MOVE (AUTO‑MOVE TOWARD CLOSEST ENEMY BATTLESHIP)
    # ---------------------------------------------------------
    def before_move(self, board_obj):
        """
        Called by Game BEFORE this piece would move.
        Torpedo automatically moves 1 square toward the closest enemy Battleship.
        If blocked → explode.
        If reaching last rank or the Battleship → explode.
        """

        board = board_obj.board

        # 1) Find closest enemy Battleship
        target_bs = board_obj.find_closest_enemy_battleship(self)

        srow = self.row
        scol = self.col
        if target_bs:
            # Compute direction vector toward Battleship
            dx = target_bs.row - srow
            dy = target_bs.col - scol

            # Normalize to a single step
            step_row = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_col = 0 if dy == 0 else (1 if dy > 0 else -1)

            next_row = srow + step_row
            next_col = scol + step_col

        else:
            # Fallback: move straight forward, 
            # win condition should prevent that situation
            target_bs = board_obj.find_closest_enemy_battleship(self)
            direction = -1 if self.color == "White" else 1
            next_row = srow + direction
            next_col = scol

        # 2) Out of bounds → explode
        if not (0 <= next_row < 8 and 0 <= next_col < 8):
            return self.explode(board_obj, srow, scol)

        target = board[next_row][next_col]

        # 3) Blocked → explode and destroy target
        if target != 0:
            return self.explode(board_obj, next_row, next_col)

        # 4) Move forward
        board[next_row][next_col] = self
        board[srow][scol] = 0
        self.row = next_row
        self.col = next_col

        # ---------------------------------------------------------
        # BUILD MOVE NOTATION
        # ---------------------------------------------------------
        move_obj = Move(
            piece=self,
            start=(srow, scol),
            end=(next_row, next_col),
            capture=None,
            transform=MoveTransform.NONE,
            result_piece=None
        )
        
        return move_obj

    def undo_before_move(self, board_obj, move_obj):
        """
        Undo a Torpedo auto-move.
        move_obj.start = original square
        move_obj.end   = square it moved to (or exploded on)
        move_obj.capture = piece destroyed by explosion (if any)
        """

        board = board_obj.board

        fr, fc = move_obj.start
        tr, tc = move_obj.end

        # 1) Remove whatever is currently on the Torpedo's destination square
        board[tr][tc] = 0

        # 2) Restore Torpedo to its original square
        board[fr][fc] = self
        self.row = fr
        self.col = fc
        board_obj.find_all_torpedo()

        # 3) Restore any captured piece (explosion victim)
        if move_obj.capture:
            victim = move_obj.capture
            board[tr][tc] = victim
            victim.row = tr
            victim.col = tc
            if isinstance(victim, Battleship):
                board_obj.find_all_battleship()
        



    # ---------------------------------------------------------
    # EXPLOSION LOGIC
    # ---------------------------------------------------------
    def explode(self, board_obj, row, col):
        """
        Removes the Torpedo and any piece on the explosion square.
        """

        board = board_obj.board
        target = board[row][col]

        # Remove target and Torpedo
        board[row][col] = 0
        board[self.row][self.col] = 0

        if isinstance(target, Battleship):
            board_obj.find_all_battleship()
        board_obj.find_all_torpedo()

        # ---------------------------------------------------------
        # BUILD MOVE NOTATION
        # ---------------------------------------------------------
        move_obj = Move(
            piece=self,
            start=(self.row, self.col),
            end=(row, col),
            capture=target,
            transform=MoveTransform.NONE,
            result_piece=None
        )

        return move_obj


