from game.move import Move


class HalfTurn:
    """
    Represents a single half-turn in Galactic Conflict.
    Contains:
      - The main move (a Move object)
      - A list of Torpedo auto-moves (each also a Move object)
    """

    def __init__(self, main_move: Move = None):
        # The primary move of the acting piece (Fighter, Corvette, etc.)
        self.main_move = main_move

        # List of Move objects representing Torpedo auto-movements
        self.torpedo_moves = []

    # ---------------------------------------------------------
    # ADDING MOVES
    # ---------------------------------------------------------

    def set_main_move(self, move: Move):
        """Assign the main move of this half-turn."""
        self.main_move = move

    def add_torpedo_move(self, move: Move):
        """Append a Torpedo auto-move to this half-turn."""
        self.torpedo_moves.append(move)

    # ---------------------------------------------------------
    # ACCESSORS
    # ---------------------------------------------------------

    def get_main_move(self):
        return self.main_move

    def get_torpedo_moves(self):
        return self.torpedo_moves

    # ---------------------------------------------------------
    # STRING REPRESENTATION
    # ---------------------------------------------------------

    def __str__(self):
        """
        Returns a readable representation:
        Example:
            TP d5-d4 FT e2-e4
        """

        lines = []

        # Torpedo moves first (they happen before the main move)
        for tm in self.torpedo_moves:
            lines.append(str(tm))

        # Then the main move
        if self.main_move:
            lines.append(str(self.main_move))

        return " ".join(lines)
