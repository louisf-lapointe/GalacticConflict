from game.half_turn import HalfTurn
from pieces.fighter import Fighter
from pieces.corvette import Corvette
from pieces.interceptor import Interceptor
from pieces.bomber import Bomber
from pieces.dreadnought import Dreadnought
from pieces.battleship import Battleship
from pieces.torpedo import Torpedo


class Human(object):
    def __init__(self, color, game):
        self.color = color
        self.game = game
        self.selected_piece = None
        self.valid_moves = []

    # ---------------------------------------------------------
    # SELECTION HANDLING
    # ---------------------------------------------------------

    def select(self, row, col, mouse_xy, ai_thinking=False):
        """
        Handles:
        - Selecting a piece
        - Attempting a move
        - Clicking UI buttons
        - Changing theme
        """

        # -------------------------------
        # 1) Board click (not UI)
        # -------------------------------
        if row < 8 and col < 8 and not ai_thinking:

            # If a piece is already selected → try to move it
            if self.selected_piece:
                result = self.move(row, col)
                if not result:
                    self.selected_piece = None
                    self.valid_moves = []

            # Select a new piece
            piece = self.game.board.get_piece(row, col)
            if piece and piece.color == self.game.turn:
                if isinstance(piece, (Fighter, Corvette, Interceptor,
                                      Bomber, Dreadnought, Battleship, Torpedo)):
                    self.selected_piece = piece
                    self.game.update_all_valid_moves()
                    self.valid_moves = piece.valid_moves
                    return True

        # -------------------------------
        # 2) Theme buttons
        # -------------------------------
        if 500 < mouse_xy[0] < 560 and 115 < mouse_xy[1] < 175:
            self.game.theme = 0

        elif 570 < mouse_xy[0] < 630 and 115 < mouse_xy[1] < 175:
            self.game.theme = 1

        elif 640 < mouse_xy[0] < 700 and 115 < mouse_xy[1] < 175:
            self.game.theme = 2

        # -------------------------------
        # 3) Game buttons
        # -------------------------------
        # Resign
        if 485 < mouse_xy[0] < 555 and 200 < mouse_xy[1] < 235:
            self.game.resign = True
            self.game.update_screen(self.valid_moves, self.game.board)

        # Toggle AI visualization
        elif 565 < mouse_xy[0] < 635 and 200 < mouse_xy[1] < 235:
            self.game.board.show_AI_calculations = not self.game.board.show_AI_calculations
            self.game.update_screen(self.valid_moves, self.game.board)

        # AI speed
        elif 565 < mouse_xy[0] < 635 and 245 < mouse_xy[1] < 280:
            if self.game.board.AI_speed == "Fast":
                self.game.board.AI_speed = "Medium"
            elif self.game.board.AI_speed == "Medium":
                self.game.board.AI_speed = "Slow"
            else:
                self.game.board.AI_speed = "Fast"
            self.game.update_screen(self.valid_moves, self.game.board)

        # Toggle valid move highlighting
        elif 645 < mouse_xy[0] < 715 and 200 < mouse_xy[1] < 235:
            self.game.board.show_valid_moves = not self.game.board.show_valid_moves
            self.game.update_screen(self.valid_moves, self.game.board)

        # Save and Load
        elif 485 < mouse_xy[0] < 555 and 245 < mouse_xy[1] < 280:
            self.game.save_to_json("./save/save.json")
        elif 645 < mouse_xy[0] < 715 and 245 < mouse_xy[1] < 280:
            self.game.load_from_json("./save/save.json")

        return False

    # ---------------------------------------------------------
    # MOVEMENT HANDLING
    # ---------------------------------------------------------

    def move(self, row, col):
        """
        Handles:
        - Normal movement
        - Captures
        - Special GC transformations (via after_move)
        """

        board = self.game.board
        piece_at_dest = board.get_piece(row, col)
        moving_piece = self.selected_piece
       
        prev_row = moving_piece.row
        prev_col = moving_piece.col

        # Illegal move
        found = False
        for amove in self.selected_piece.valid_moves:
          if amove.row() == row and amove.col() == col:
              found = True
              break
        
        if not found:
          return False

        is_capture = piece_at_dest != 0 and piece_at_dest.color != moving_piece.color

        # ---------------------------------------------------------
        # CAPTURE
        # ---------------------------------------------------------
        if is_capture:
            self.game.capture(piece_at_dest)

        # -------------------------------
        # MOVE THE PIECE
        # -------------------------------


        ht_obj = board.move(self.selected_piece.row, self.selected_piece.col, row, col)


        ht_str = str(ht_obj)
        self.game.move_history.move_log.append(ht_str)
        self.game.board.previous_move = ht_obj
        self.game.update_game()
        self.game.check_game_status()

        # Reset selection
        self.selected_piece = None
        self.valid_moves = []

        # Update screen
        #self.game.computer.reset_visualizer_stats()
        self.game.update_screen(self.valid_moves, self.game.board)

        return True