from pieces.piece import Piece
from game.move import Move, MoveTransform
import pygame

# Load images
white_corvette = pygame.image.load("pieces/assets/White_Corvette.png")
black_corvette = pygame.image.load("pieces/assets/Black_Corvette.png")
Corvette_images = [white_corvette, black_corvette]


# Optional: piece-square table (knight-like)
white_corvette_eval_table = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

black_corvette_eval_table = white_corvette_eval_table[::-1]


class Corvette(Piece):
    images = Corvette_images

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.valid_moves = []
        self.letter = "CV"

    # ---------------------------------------------------------
    # VALID MOVES (knight-like jumping)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        self.valid_moves = self.get_valid_moves(board)
        return self.valid_moves

    def get_valid_moves(self, board):
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1)
        ]

        for dx, dy in knight_moves:
            row = self.row + dx
            col = self.col + dy

            if 0 <= row < 8 and 0 <= col < 8:
                piece = board[row][col]
                if piece == 0 or piece.color != self.color:
                    moves.append(Move(self, (self.row, self.col), (row, col), piece != 0, MoveTransform.NONE))
                elif piece != 0 and piece.color == self.color and isinstance(piece, Corvette):
                    moves.append(Move(self, (self.row, self.col), (row, col), False, MoveTransform.COUPLE))

        return moves

    def move(self, board_obj, row, col):
        board = board_obj.board
        target = board[row][col]

        from pieces.corvette import Corvette
        from pieces.battleship import Battleship

        # Friendly Corvette → Battleship
        if isinstance(target, Corvette) and target.color == self.color:
            board_obj.board[self.row][self.col] = 0
            board[row][col] = Battleship(row, col, self.color)
            board_obj.find_all_battleship()
            return


        """Update internal coordinates when the board moves the piece."""
        if board_obj.board[self.row][self.col] != 0:
            board_obj.board[row][col] = board_obj.board[self.row][self.col]
        board_obj.board[self.row][self.col] = 0
        
        if board_obj.board[row][col] != 0:
            board_obj.board[row][col].row = row
            board_obj.board[row][col].col = col
