from game.move_transform import MoveTransform

class Move:
    """
    Builds a proper string representation of a Galactic Conflict move.
    This class is intentionally simple and engine‑agnostic.
    """

    FILES = "abcdefgh"

    def __init__(self, piece, start, end, capture=None,
                 transform=MoveTransform.NONE, result_piece=None):
        """
        piece:       Piece object BEFORE the move
        start:       (row, col)
        end:         (row, col)
        capture:     Piece if captured
        transform:   String describing special rule:
                     "promotion", "demotion", "decouple_bm",
                     "decouple_in", "couple", "boarding"
        result_piece: Piece object AFTER transformation (if any)
        """

        self.piece = piece
        self.start = start
        self.end = end
        self.capture = capture
        self.transform = transform
        self.result_piece = result_piece

    def row(self):
        return self.end[0]

    def col(self):
        return self.end[1]

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def square_to_str(self, row, col):
        """Convert (row, col) → algebraic square like 'e4'."""
        file = Move.FILES[col]
        rank = 8 - row
        return f"{file}{rank}"

    # ---------------------------------------------------------
    # MAIN STRING BUILDER
    # ---------------------------------------------------------

    def __str__(self):
        start_sq = self.square_to_str(*self.start)
        end_sq = self.square_to_str(*self.end)

        letter = self.piece.letter

        # -------------------------------
        # BASIC MOVE OR CAPTURE
        # -------------------------------
        if self.capture:
            base = f"{letter} {start_sq}x{end_sq}"
        else:
            base = f"{letter} {start_sq}-{end_sq}"

        # -------------------------------
        # SPECIAL TRANSFORMATIONS
        # -------------------------------
        if self.transform == MoveTransform.NONE:
            return base

        # Fighter → Torpedo
        if self.transform == MoveTransform.PROMOTION:
            return f"{base}={self.result_piece.letter}"

        # Battleship → Dreadnought
        if self.transform == MoveTransform.DEMOTION:
            return f"{base}>{self.result_piece.letter}"

        # Battleship → Corvette + Corvette
        if self.transform == MoveTransform.DECOUPLE_CV:
            return f"{base}>{self.result_piece.letter}"

        # Corvette + Corvette → Battleship
        if self.transform == MoveTransform.MERGE and self.result_piece.letter == "BS":
            return f"{base}={self.result_piece.letter}"

        # DN → Bomber (origin) + Interceptor (dest)
        if self.transform == MoveTransform.DECOUPLE_BM:
            return f"{base}>{self.result_piece.letter}"

        # DN → Interceptor (origin) + Bomber (dest)
        if self.transform == MoveTransform.DECOUPLE_IN:
            return f"{base}>{self.result_piece.letter}"

        # Bomber + Interceptor → Dreadnought
        if self.transform == MoveTransform.COUPLE:
            return f"{base}={self.result_piece.letter}"

        # Interceptor + enemy Bomber → Dreadnought
        if self.transform == MoveTransform.BOARDING:
            return f"{base}x{self.result_piece.letter}"

        # Fallback
        return base