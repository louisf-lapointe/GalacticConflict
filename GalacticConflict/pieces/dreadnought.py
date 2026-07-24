from pieces.piece import Piece
from game.move import Move, MoveTransform
import pygame

# Load images
white_dreadnought = pygame.image.load("pieces/assets/White_Dreadnought.png")
black_dreadnought = pygame.image.load("pieces/assets/Black_Dreadnought.png")
Dreadnought_images = [white_dreadnought, black_dreadnought]


# Optional: piece-square table (queen-like)
white_dreadnought_eval_table = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10,   0,   0,  0,  0,   0,   0, -10,
    -10,   0,   5,  5,  5,   5,   0, -10,
     -5,   0,   5,  10,  10,   5,   0,  -5,
      0,   0,   5,  10,  10,   5,   0,   0,
    -10,   5,   5,  5,  5,   5,   5, -10,
    -10,   0,   5,  0,  0,   0,   0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

black_dreadnought_eval_table = white_dreadnought_eval_table[::-1]


class Dreadnought(Piece):
    images = Dreadnought_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "DN"

    # ---------------------------------------------------------
    # VALID MOVES (queen-like sliding)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),      # orthogonal
            (-1, -1), (-1, 1), (1, -1), (1, 1)     # diagonal
        ]

        for dx, dy in directions:
            row, col = self.row, self.col
            firstSquare = True
            while True:
                row += dx
                col += dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                piece = board[row][col]

                if piece != 0:
                    if piece.color != self.color:
                        moves.append(Move(self, (self.row, self.col), (row, col), True, MoveTransform.NONE))  # capture
                    break

                if firstSquare:
                    if abs(dx) == abs(dy):
                        moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.DECOUPLE_IN))
                    else:
                        moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.DECOUPLE_BM))
                else:
                    moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.NONE))
                firstSquare = False

        return moves
    
    # ---------------------------------------------------------
    # SPECIAL MOVES: Decoupling
    # ---------------------------------------------------------
    def move(self, board_obj, row, col):
        """
        Handles:
        - Bomber Decoupling (orthogonal 1-step)
        - Interceptor Decoupling (diagonal 1-step)
        """

        board = board_obj.board

        from pieces.bomber import Bomber
        from pieces.interceptor import Interceptor

        piece = board[row][col]
        dx = row - self.row
        dy = col - self.col

        # -----------------------------------------------------
        # 1) Bomber Decoupling (orthogonal 1-step)
        # -----------------------------------------------------
        if abs(dx) + abs(dy) == 1 and piece == 0:  # exactly one square orthogonally
            # Replace origin with Interceptor
            board[self.row][self.col] = Interceptor(self.row, self.col, self.color)
            # Arrival square becomes Bomber
            board[row][col] = Bomber(row, col, self.color)
            return

        # -----------------------------------------------------
        # 2) Interceptor Decoupling (diagonal 1-step)
        # -----------------------------------------------------
        if abs(dx) == 1 and abs(dy) == 1 and piece == 0:  # exactly one square diagonally
            # Replace origin with Bomber
            board[self.row][self.col] = Bomber(self.row, self.col, self.color)
            # Arrival square becomes Interceptor
            board[row][col] = Interceptor(row, col, self.color)
            return

        board[row][col] = board_obj.board[self.row][self.col]
        board[self.row][self.col] = 0
        if board[row][col] != 0:
            board[row][col].row = row
            board[row][col].col = col
