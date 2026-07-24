from pieces.piece import Piece
from game.move import Move, MoveTransform
import pygame

# Load images
white_bomber = pygame.image.load("pieces/assets/White_Bomber.png")
black_bomber = pygame.image.load("pieces/assets/Black_Bomber.png")
Bomber_images = [white_bomber, black_bomber]


# Optional: Piece-square table (rook-like)
white_bomber_eval_table = [
    0,  0,  0,  5,  5,  0,  0,  0,
    0, 10, 10, 10, 10, 10, 10,  0,
    0, 10, 15, 15, 15, 15, 10,  0,
    5, 10, 15, 20, 20, 15, 10,  5,
    5, 10, 15, 20, 20, 15, 10,  5,
    0, 10, 15, 15, 15, 15, 10,  0,
    0, 10, 10, 10, 10, 10, 10,  0,
    0,  0,  0,  5,  5,  0,  0,  0
]

black_bomber_eval_table = white_bomber_eval_table[::-1]


class Bomber(Piece):
    images = Bomber_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "BM"

    # ---------------------------------------------------------
    # VALID MOVES (rook-like sliding)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # vertical + horizontal

        for dx, dy in directions:
            row, col = self.row, self.col
            while True:
                row += dx
                col += dy

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                piece = board[row][col]

                if piece != 0:
                    if piece.color != self.color:
                        moves.append(Move(self, (self.row, self.col), (row, col), True, MoveTransform.NONE))  # capture
                    elif isinstance(piece, Interceptor):
                        moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.COUPLE))
                    break

                moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.NONE))

        return moves

    # ---------------------------------------------------------
    # SPECIAL MOVE
    # ---------------------------------------------------------

    def move(self, board_obj, row, col):
        """
        Handles:
        - Dreadnought Coupling (merge with friendly Interceptor)
        """

        board = board_obj.board
        target = board[row][col]

        from pieces.interceptor import Interceptor
        from pieces.dreadnought import Dreadnought

        # Friendly Interceptor → Dreadnought
        if isinstance(target, Interceptor) and target.color == self.color:
            board[self.row][self.col] = 0
            board[row][col] = Dreadnought(row, col, self.color)
        else:
            board[row][col] = board_obj.board[self.row][self.col]
            board[self.row][self.col] = 0
            if board[row][col] != 0:
                board[row][col].row = row
                board[row][col].col = col

        


from pieces.interceptor import Interceptor