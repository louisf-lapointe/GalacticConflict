from pieces.piece import Piece
from game.move import Move, MoveTransform
import pygame

# Load images
white_battleship = pygame.image.load("pieces/assets/White_Battleship.png")
black_battleship = pygame.image.load("pieces/assets/Black_Battleship.png")
Battleship_images = [white_battleship, black_battleship]


# Optional: piece-square table (king-like)
white_battleship_eval_table = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
]

black_battleship_eval_table = white_battleship_eval_table[::-1]


class Battleship(Piece):
    images = Battleship_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "BS"

    # ---------------------------------------------------------
    # VALID MOVES (king-like)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1),  (1, 0), (1, 1),
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1)
        ]

        for dx, dy in directions:
            row = self.row + dx
            col = self.col + dy

            if 0 <= row < 8 and 0 <= col < 8:
                piece = board[row][col]
                if piece == 0 or piece.color != self.color:
                    if abs(dx) == 2 or abs(dy) == 2:
                        moves.append(Move(self, (self.row, self.col), (row, col), piece != 0, MoveTransform.DECOUPLE_CV))
                    else:
                        moves.append(Move(self, (self.row, self.col), (row, col), piece != 0, MoveTransform.NONE))
                elif dx == 0 and dy == 0:
                    moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.DEMOTION))

        return moves

    # ---------------------------------------------------------
    # SPECIAL MOVES: Demotion + Corvette Decoupling
    # ---------------------------------------------------------
    def move(self, board_obj, row, col):
        board = board_obj.board

        from pieces.dreadnought import Dreadnought
        from pieces.corvette import Corvette

        dx = row - self.row
        dy = col - self.col

        # -----------------------------------------------------
        # 2) Corvette Decoupling (horizontal 1-step)
        # -----------------------------------------------------
        if abs(dx) == 2 or abs(dy) == 2:
            # Origin becomes Corvette
            board[self.row][self.col] = Corvette(self.row, self.col, self.color)
            # Destination becomes Corvette
            board[row][col] = Corvette(row, col, self.color)
            board_obj.find_all_battleship()
            return

        if dx == 0 and dy == 0:
            # Transform into a Dreadnough
            board[row][col] = Dreadnought(row, col, self.color)
            board_obj.find_all_battleship()
            return

        """Update internal coordinates when the board moves the piece."""
        board_obj.board[row][col] = board_obj.board[self.row][self.col]
        board_obj.board[self.row][self.col] = 0
        if board_obj.board[row][col] != 0:
            board_obj.board[row][col].row = row
            board_obj.board[row][col].col = col
