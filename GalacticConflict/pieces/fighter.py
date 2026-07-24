from pieces.piece import Piece
from pieces.torpedo import Torpedo
from game.move import Move, MoveTransform
import pygame

# Load images
white_fighter = pygame.image.load("pieces/assets/White_Fighter.png")
black_fighter = pygame.image.load("pieces/assets/Black_Fighter.png")
Fighter_images = [white_fighter, black_fighter]


# Optional: piece-square table (pawn-like)
black_fighter_eval_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    5, 5, 5,  5, 5, 5, 5,  5,
    0,  0,  30, 30, 30,  15,  0,  0,
    5,  10, 30, 40, 40, 30,  10,  5,
    10, 10, 25, 30, 30, 25, 10, 10,
    50, 50, 20, 20, 20, 20, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]

white_fighter_eval_table = black_fighter_eval_table[::-1]


class Fighter(Piece):
    images = Fighter_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "FT"

    # ---------------------------------------------------------
    # VALID MOVES (pawn-like)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []

        direction = -1 if self.color == "White" else 1
        start_row = 6 if self.color == "White" else 1
        last_rank = 0 if self.color == "White" else 7

        # 1-square forward
        if board[self.row + direction][self.col] == 0:
            if self.row + direction == last_rank:
                moves.append(Move(self, (self.row, self.col), (self.row + direction, self.col), False, MoveTransform.PROMOTION))
            else:
                moves.append(Move(self, (self.row, self.col), (self.row + direction, self.col), False, MoveTransform.NONE))

            # 2-square forward
            if self.row == start_row and board[self.row + 2 * direction][self.col] == 0:
                moves.append(Move(self, (self.row, self.col), (self.row + 2 * direction, self.col), False, MoveTransform.NONE))

        # Diagonal captures
        for dc in [-1, 1]:
            c = self.col + dc
            r = self.row + direction
            if 0 <= c < 8 and 0 <= r < 8:
                target = board[r][c]
                if target != 0 and target.color != self.color:
                    if r == last_rank:
                        moves.append(Move(self, (self.row, self.col), (r, c), True, MoveTransform.PROMOTION))
                    else:
                        moves.append(Move(self, (self.row, self.col), (r, c), True, MoveTransform.NONE))

        return moves

    # ---------------------------------------------------------
    # SPECIAL MOVE: Promotion → Torpedo
    # ---------------------------------------------------------
    def move(self, board_obj, row, col):
        """Update internal coordinates when the board moves the piece."""
        board = board_obj.board
        board[row][col] = board_obj.board[self.row][self.col]
        board[self.row][self.col] = 0
        if board[row][col] != 0:
            board[row][col].row = row
            board[row][col].col = col

        
        last_rank = 0 if self.color == "White" else 7
        # Promotion to Torpedo
        if row == last_rank:
            board[row][col] = Torpedo(row, col, self.color)
            board_obj.find_all_torpedo()