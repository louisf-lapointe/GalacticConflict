
from pieces.piece import Piece
from game.move import Move, MoveTransform
import pygame

# Load images
white_interceptor = pygame.image.load("pieces/assets/White_Interceptor.png")
black_interceptor = pygame.image.load("pieces/assets/Black_Interceptor.png")
Interceptor_images = [white_interceptor, black_interceptor]


# Optional: Piece-square table (kept bishop-like for now)
white_interceptor_eval_table = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

black_interceptor_eval_table = white_interceptor_eval_table[::-1]


class Interceptor(Piece):
    images = Interceptor_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "IN"

    # ---------------------------------------------------------
    # VALID MOVES (diagonal sliding)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

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
                        if isinstance(piece, Bomber):
                            moves.append(Move(self, (self.row, self.col), (row, col), True, MoveTransform.BOARDING)) # boarding
                        else:
                            moves.append(Move(self, (self.row, self.col), (row, col), True, MoveTransform.NONE))  # capture
                    elif isinstance(piece, Bomber):
                            moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.COUPLE)) 
                    break

                moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.NONE))

        return moves

    # ---------------------------------------------------------
    # SPECIAL MOVES 
    # ---------------------------------------------------------

    def move(self, board_obj, row, col):
        """
        Handles:
        - Dreadnought Coupling (merge with friendly Bomber)
        - Boarding (merge with enemy Bomber)
        """

        board = board_obj.board
        target = board[row][col]

        # Friendly Bomber → Dreadnought
        from pieces.bomber import Bomber
        from pieces.dreadnought import Dreadnought

        if isinstance(target, Bomber) and target.color == self.color:
            # Coupling
            board[self.row][self.col] = 0
            board[row][col] = Dreadnought(row, col, self.color)

        # Enemy Bomber → Dreadnought (Boarding)
        elif isinstance(target, Bomber) and target.color != self.color:
            board[self.row][self.col] = 0
            board[row][col] = Dreadnought(row, col, self.color)
        else:
            board[row][col] = board_obj.board[self.row][self.col]
            board[self.row][self.col] = 0
            if board[row][col] != 0:
                board[row][col].row = row
                board[row][col].col = col


from pieces.bomber import Bomber