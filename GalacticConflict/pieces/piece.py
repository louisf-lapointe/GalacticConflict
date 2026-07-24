from game.constants import square_size


class Piece(object):
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.type = self.__class__.__name__
        self.selected = False
        self.valid_moves = []
        self.letter = "?"   # Each subclass overrides this

    # ---------------------------------------------------------
    # BASIC STATE
    # ---------------------------------------------------------

    def is_selected(self):
        return self.selected

    def move(self, board_obj, row, col):
        """Update internal coordinates when the board moves the piece."""
        board_obj.board[row][col] = board_obj.board[self.row][self.col]
        board_obj.board[self.row][self.col] = 0
        if board_obj.board[row][col] != 0:
            board_obj.board[row][col].row = row
            board_obj.board[row][col].col = col


    # ---------------------------------------------------------
    # DRAWING
    # ---------------------------------------------------------

    def draw(self, window, image, player_color):
        """
        Draws the piece on the board.
        Board flips if the player is Black.
        """
        if player_color == "White":
            x = self.col * square_size
            y = self.row * square_size
        else:
            x = (7 - self.col) * square_size
            y = (7 - self.row) * square_size

        window.blit(image, (x, y))

    # ---------------------------------------------------------
    # MOVE GENERATION (overridden by subclasses)
    # ---------------------------------------------------------

    def update_valid_moves(self, board):
        """
        Each subclass implements its own movement rules.
        """
        return []

    # ---------------------------------------------------------
    # SPECIAL MOVE HOOKS
    # ---------------------------------------------------------

    def before_move(self, board_obj):
        """
        Called BEFORE the piece is moved on the board.
        Subclasses override this to implement:
        - Torpedo displacement
        """
        pass

    def undo_before_move(self, board_obj, move_obj):
        """
        Called after the piece is un-moved on the board.
        Subclasses override this to implement:
        - Undo of Torpedo displacement
        """
        pass

    # ---------------------------------------------------------
    # SPECIAL MOVE HOOKS
    # ---------------------------------------------------------

    def after_move(self, board_obj, row, col):
        """
        Called AFTER the piece is moved on the board.
        Subclasses override this to implement:
        - Decoupling
        - Demotion
        - Promotions
        - Coupling
        - Boarding
        """
        pass
