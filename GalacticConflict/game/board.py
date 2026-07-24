import pygame
import json
from game.constants import square_size, num_rows, num_cols, light_gray, images
from game.move import Move
from game.move_transform import MoveTransform

from game.half_turn import HalfTurn

# Import Galactic Conflict pieces
from pieces.battleship import Battleship, Battleship_images
from pieces.dreadnought import Dreadnought, Dreadnought_images
from pieces.bomber import Bomber, Bomber_images
from pieces.interceptor import Interceptor, Interceptor_images
from pieces.corvette import Corvette, Corvette_images
from pieces.fighter import Fighter, Fighter_images
from pieces.torpedo import Torpedo, Torpedo_images
from game.material import Material


pygame.font.init()

# Piece image dictionary
PIECE_IMAGES = {
    "Battleship": (Battleship_images[0], Battleship_images[1]),
    "Dreadnought": (Dreadnought_images[0], Dreadnought_images[1]),
    "Bomber": (Bomber_images[0], Bomber_images[1]),
    "Interceptor": (Interceptor_images[0], Interceptor_images[1]),
    "Corvette": (Corvette_images[0], Corvette_images[1]),
    "Fighter": (Fighter_images[0], Fighter_images[1]),
    "Torpedo": (Torpedo_images[0], Torpedo_images[1])
}
PIECE_CLASS_MAP = {
    "Fighter": Fighter,
    "Corvette": Corvette,
    "Interceptor": Interceptor,
    "Bomber": Bomber,
    "Dreadnought": Dreadnought,
    "Battleship": Battleship,
    "Torpedo": Torpedo,
}


class Board(object):
    def __init__(self, player_color):
        self.player_color = player_color
        self.move_notation = ""
        self.show_valid_moves = True
        self.show_AI_calculations = False
        self.AI_speed = "Fast"
        self.stored_moves = []
        self.previous_move = None
        self.prev_square = None
        self.piece = None
        self.target = None
        self.captured_piece = 0
        self.material = Material()
        self.white_torpedo = []
        self.black_torpedo = []
        self.white_battleship = []
        self.black_battleship = []

        # 8×8 board
        self.board = [[0 for _ in range(8)] for _ in range(8)]

    # ---------------------------------------------------------
    # BASIC BOARD OPERATIONS
    # ---------------------------------------------------------

    def move(self, srow, scol, row, col):

        # Half Turn object
        ht_obj = HalfTurn()

        #piece
        piece = self.get_piece(srow, scol)

        # Handle all pieces that moves before this move, for torpedo
        if piece.color == "White":
            for torp in self.white_torpedo:
                ht_obj.add_torpedo_move(torp.before_move(self))
        else:
            for torp in self.black_torpedo:
                ht_obj.add_torpedo_move(torp.before_move(self))

        """Move a piece and handle special Galactic Conflict rules."""
        target = self.board[row][col]
        start_row = piece.row
        start_col = piece.col
        piece.move(self, row, col)

        if isinstance(target, Torpedo):
           self.find_all_torpedo()
        if isinstance(target, Battleship):
            self.find_all_battleship()


         # After transformation, the piece on the square may be different
        before_type = piece.type
        piece_after = self.get_piece(row, col)
        if piece_after != 0 and piece_after != None:
            after_type = piece_after.type
        else:
            after_type = before_type

        # ---------------------------------------------------------
        # DETERMINE TRANSFORMATION TYPE
        # ---------------------------------------------------------
        transform = MoveTransform.NONE

        if before_type != after_type:
            # Fighter → Torpedo
            if before_type == "Fighter" and after_type == "Torpedo":
                transform = MoveTransform.PROMOTION

            # Battleship → Dreadnought
            elif before_type == "Battleship" and after_type == "Dreadnought":
                transform = MoveTransform.DEMOTION

            # Battleship -> Corvette + Corvette
            elif before_type == "Battleship" and after_type == "Corvette":
                transform = MoveTransform.DECOUPLE_CV

            # Corvette + Corvette → Battleship
            elif before_type == "Corvette" and after_type == "Battleship":
                transform = MoveTransform.MERGE

            # Dreadnought decoupling
            elif before_type == "Dreadnought" and after_type == "Bomber":
                transform = MoveTransform.DECOUPLE_BM
            elif before_type == "Dreadnought" and after_type == "Interceptor":
                transform = MoveTransform.DECOUPLE_IN

             # Boarding (IN + enemy BM → DN)
            elif before_type == "Interceptor" and after_type == "Dreadnought" and target.color != piece_after.color:
                transform = MoveTransform.BOARDING

            # Coupling (BM + IN → DN)
            elif after_type == "Dreadnought" and before_type in ("Bomber", "Interceptor"):
                transform = MoveTransform.COUPLE
           

         
        move_obj = Move(
            piece=piece,
            start=(start_row, start_col),
            end=(row, col),
            capture=target,
            transform=transform,
            result_piece=piece_after
        )
        ht_obj.main_move = move_obj

        return ht_obj

    def undo_move(self):
    #
    #Undo a move including ALL Galactic Conflict transformations.
    #Uses the HalfTurn object stored in self.stored_moves.
    #

        move_data = self.stored_moves.pop()

        main = move_data.main_move
        piece_before = main.piece
        piece_after  = main.result_piece
        from_sq      = main.start
        to_sq        = main.end
        captured     = main.capture
        transform    = main.transform

        fr, fc = from_sq
        tr, tc = to_sq

        # ---------------------------------------------------------
        # 1) REMOVE PIECE FROM DESTINATION SQUARE
        # ---------------------------------------------------------
        self.board[tr][tc] = 0

        # ---------------------------------------------------------
        # 2) RESTORE ORIGINAL PIECE TO ORIGINAL SQUARE
        # ---------------------------------------------------------
        piece_before.row = fr
        piece_before.col = fc
        self.board[fr][fc] = piece_before

        # ---------------------------------------------------------
        # 3) RESTORE CAPTURED PIECE (if any)
        # ---------------------------------------------------------
        if captured:
            self.board[tr][tc] = captured
            captured.row = tr
            captured.col = tc

            # Rebuild caches if needed
            if isinstance(captured, Torpedo):
                self.find_all_torpedo()
            if isinstance(captured, Battleship):
                self.find_all_battleship()

        # ---------------------------------------------------------
        # 4) REVERSE SPECIAL TRANSFORMATIONS
        # ---------------------------------------------------------

        if transform == MoveTransform.PROMOTION:
            # Torpedo → Fighter
            self.board[fr][fc] = piece_before
            self.find_all_torpedo()

        elif transform == MoveTransform.DEMOTION:
            # Dreadnought → Battleship
            self.board[fr][fc] = piece_before
            self.find_all_battleship()

        elif transform == MoveTransform.DECOUPLE_CV:
            # Battleship -> Corvette and Corvette
            self.board[fr][fc] = Battleship(fr, fc, piece_before.color)
            self.find_all_battleship()

        elif transform == MoveTransform.MERGE:
            # Battleship → two Corvettes
            self.board[fr][fc] = Corvette(fr, fc, piece_before.color)
            self.board[tr][tc] = Corvette(tr, tc, piece_before.color)
            self.find_all_battleship()

        elif transform == MoveTransform.DECOUPLE_BM:
            # DN → Bomber + Interceptor
            self.board[fr][fc] = piece_before
            self.board[tr][tc] = captured if captured else 0

        elif transform == MoveTransform.DECOUPLE_IN:
            # DN → Interceptor + Bomber
            self.board[fr][fc] = piece_before
            self.board[tr][tc] = captured if captured else 0

        elif transform == MoveTransform.COUPLE:
            # Bomber + Interceptor → Dreadnought
            if isinstance(main.piece, Bomber):
                self.board[fr][fc] = Bomber(fr, fc, piece_before.color)
                self.board[tr][tc] = Interceptor(tr, tc, piece_before.color)
            else:
                self.board[fr][fc] = Interceptor(fr, fc, piece_before.color)
                self.board[tr][tc] = Bomber(tr, tc, piece_before.color)

        elif transform == MoveTransform.BOARDING:
            # Interceptor + enemy Bomber → Dreadnought
            interceptor = piece_before
            enemy_bomber = captured
            self.board[fr][fc] = interceptor
            self.board[tr][tc] = enemy_bomber

        # ---------------------------------------------------------
        # 5) CLEAR BOARD STATE
        # ---------------------------------------------------------
        self.captured_piece = 0

        # ---------------------------------------------------------
        # 6) UNDO ALL TORPEDO AUTO-MOVES
        # ---------------------------------------------------------
        for tp_move in reversed(move_data.torpedo_moves):
            tp_piece = tp_move.piece
            tp_piece.undo_before_move(self, tp_move)


    def get_piece(self, row, col):
        return self.board[row][col]

    # ---------------------------------------------------------
    # INITIAL SETUP (Galactic Conflict)
    # ---------------------------------------------------------

    def initiate_pieces(self):
        """Place all Galactic Conflict pieces in starting positions."""

        # White setup (bottom)
        white_back = [
            Bomber(7, 0, "White"), Corvette(7, 1, "White"),
            Interceptor(7, 2, "White"), Dreadnought(7, 3, "White"),
            Battleship(7, 4, "White"), Interceptor(7, 5, "White"),
            Corvette(7, 6, "White"), Bomber(7, 7, "White")
        ]
        white_fighters = [Fighter(6, c, "White") for c in range(8)]

        # Black setup (top)
        black_back = [
            Bomber(0, 0, "Black"), Corvette(0, 1, "Black"),
            Interceptor(0, 2, "Black"), Dreadnought(0, 3, "Black"),
            Battleship(0, 4, "Black"), Interceptor(0, 5, "Black"),
            Corvette(0, 6, "Black"), Bomber(0, 7, "Black")
        ]
        black_fighters = [Fighter(1, c, "Black") for c in range(8)]

        pieces = white_back + white_fighters + black_back + black_fighters

        for piece in pieces:
            self.board[piece.row][piece.col] = piece

        self.find_all_torpedo()
        self.find_all_battleship()
        return


    def find_all_battleship(self):
        self.white_battleship = self.get_all_battleship("White")
        self.black_battleship = self.get_all_battleship("Black")

    def find_all_torpedo(self):
        self.white_torpedo = self.get_all_torpedo("White")
        self.black_torpedo = self.get_all_torpedo("Black")

    # ---------------------------------------------------------
    # DRAWING
    # ---------------------------------------------------------

    def create_board(self, window, theme):
        """Draw the board background, coordinates, and move history area."""
        my_font = pygame.font.SysFont("calibri", 15)

        letters = ["a","b","c","d","e","f","g","h"]
        if self.player_color == "Black":
            letters.reverse()

        window.fill(theme[0])

        # Draw squares
        for row in range(num_rows):
            for col in range(num_cols):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(
                        window, theme[1],
                        (row * square_size, col * square_size, square_size, square_size)
                    )

        # Draw coordinates
        for i in range(8):
            text = my_font.render(letters[i], True, (0, 0, 0))
            window.blit(text, (square_size * i + 2, square_size * 7 + square_size - 20))

            rank = 8 - i if self.player_color == "White" else i + 1
            text = my_font.render(str(rank), True, (0, 0, 0))
            window.blit(text, (2, square_size * i + 5))

        # Move history panel
        pygame.draw.rect(window, (255, 255, 255), (10, 490, 700, 140))

    def draw(self, window, board):
        """Draw all pieces."""
        for row in board.board:
            for piece in row:
                if piece:
                    imgs = PIECE_IMAGES[type(piece).__name__]
                    img = imgs[0] if piece.color == "White" else imgs[1]
                    piece.draw(window, img, self.player_color)

    # ---------------------------------------------------------
    # VALID MOVE HIGHLIGHTING
    # ---------------------------------------------------------

    def draw_valid_moves(self, moves, window):
        for amove in moves:
            row = amove.row()
            col = amove.col()
            if self.player_color == "White":
                self.draw_move_square(col, row, [128, 5, 242], window)
            else:
                self.draw_move_square(7 - col, 7 - row, [128, 5, 242], window)

    def draw_previous_move(self, window):
        if self.previous_move:
            srow, scol = self.previous_move.main_move.start
            erow, ecol = self.previous_move.main_move.end
            if self.player_color == "White":
                self.draw_move_square(scol, srow, [21, 35, 230], window)
                self.draw_move_square(ecol, erow, [21, 35, 230], window)
            else:
                self.draw_move_square(7 - scol, 7 - srow, [21, 35, 230], window)
                self.draw_move_square(7 - ecol, 7 - erow, [21, 35, 230], window)
                    

    def draw_move_square(self, row, col, color, window):
        pygame.draw.rect(
            window, color,
            (row * square_size, col * square_size, square_size + 1, square_size + 1), 2
        )

    # ---------------------------------------------------------
    # PIECE COLLECTION
    # ---------------------------------------------------------

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces


    def draw_theme_window(self, window):
    # Blue
        window.blit(images[0], (500, 115))

    # Purple
        window.blit(images[1], (570, 115))

    # Red
        window.blit(images[2], (640, 115))


    def draw_game_buttons(self, window, theme, ai):
      my_font = pygame.font.SysFont("calibri", 12)
      
      # Resign Button
      new_game = my_font.render("Resign/Quit", True, (0, 0, 0))
      pygame.draw.rect(window, [0, 0, 0], (483, 198, 74, 39))
      pygame.draw.rect(window, [255, 255, 255], (485, 200, 70, 35))
      window.blit(new_game, (488, 210))

      # Visualize AI Button
      show_thinking = my_font.render("Visualize AI", True, (0, 0, 0))
      pygame.draw.rect(window, [0, 0, 0], (563, 198, 74, 39))
      if self.show_AI_calculations:
          pygame.draw.rect(window, theme[1], (565, 200, 70, 35))
      else:
          pygame.draw.rect(window, [255, 255, 255], (565, 200, 70, 35))
      window.blit(show_thinking, (568, 210))

      # Visualize AI Speed Button
      speed = my_font.render(self.AI_speed, True, (0, 0, 0))
      pygame.draw.rect(window, [0, 0, 0], (563, 243, 74, 39))
      if self.show_AI_calculations:
          pygame.draw.rect(window, theme[1], (565, 245, 70, 35))
      else:
          pygame.draw.rect(window, [255, 255, 255], (565, 245, 70, 35))

      if self.AI_speed == "Medium":
          window.blit(speed, (579, 255))
      else:
          window.blit(speed, (588, 255))

      # Highlight Valid Moves
      show_valid_moves1 = my_font.render("Highlight", True, (0, 0, 0))
      show_valid_moves2 = my_font.render("Valid Moves", True, (0, 0, 0))
      pygame.draw.rect(window, [0, 0, 0], (643, 198, 74, 39))
      if self.show_valid_moves:
          pygame.draw.rect(window, theme[1], (645, 200, 70, 35))
      else:
          pygame.draw.rect(window, [255, 255, 255], (645, 200, 70, 35))
      window.blit(show_valid_moves1, (655, 203))
      window.blit(show_valid_moves2, (648, 217))

      # Save and Load
      save_font = my_font.render("Save", True, (0, 0, 0))
      load_font = my_font.render("Load", True, (0, 0, 0))
      pygame.draw.rect(window, theme[1], (645, 245, 70, 35))
      pygame.draw.rect(window, theme[1], (485, 245, 70, 35))
      window.blit(save_font, (500, 255))
      window.blit(load_font, (670, 255))
      
      if not ai:
        return
      
      pruned_percentage = "N/A"
      if ai.moves_evaluated and ai.total_moves_found:
        pruned_percentage = str(round(100 - (ai.moves_evaluated / max(1, ai.total_moves_found)) * 100, 2)) + "%"
      
      # Display AI evaluation stats
      moves_evaluated_text = my_font.render(f"Moves Evaluated: {ai.moves_evaluated}", True, (0, 0, 0))
      total_moves_found_text = my_font.render(f"Total Moves Found: {ai.total_moves_found}", True, (0, 0, 0))      
      pruned_percentage_text = my_font.render(f"% of Search Tree Pruned: {pruned_percentage}", True, (0, 0, 0))
      current_best_evaluation_text = my_font.render(f"Current Best Evaluation: {round(ai.current_best_evaluation / 100, 2)}", True, (0, 0, 0))
      
      window.blit(moves_evaluated_text, (500, 310))
      window.blit(total_moves_found_text, (500, 330))
      window.blit(pruned_percentage_text, (500, 350))
      window.blit(current_best_evaluation_text, (500, 370))

    def draw_valid_moves(self, moves, window):
        for move in moves:
          row, col = move.row(), move.col()
          if self.player_color == "White":
            self.draw_move_square(col, row, [128, 5, 242], window)
          else:
            self.draw_move_square(7 - col, 7 - row, [128, 5, 242], window)

    def draw_previous_move(self, window):
        if self.previous_move is not None:
            row, col = self.previous_move.main_move.start
            if self.player_color == "White":
              self.draw_move_square(col, row, [21, 35, 230], window)
            else:
              self.draw_move_square(7 - col, 7 - row, [21, 35, 230], window)
            row, col = self.previous_move.main_move.end
            if self.player_color == "White":
              self.draw_move_square(col, row, [21, 35, 230], window)
            else:
              self.draw_move_square(7 - col, 7 - row, [21, 35, 230], window)
    
    def draw_move_square(self, row, col, color, window):
        pygame.draw.rect(window, color, (row * square_size, col *
                         square_size, square_size + 1, square_size + 1), 2)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
          for piece in row:
            if isinstance(piece, (Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo)) and piece.color == color:
              pieces.append(piece)
        return pieces

    def get_all_torpedo(self, color):
        torpedo = []
        for row in self.board:
            for piece in row:
                if isinstance(piece, (Torpedo)) and piece.color == color:
                    torpedo.append(piece)
        return torpedo

    def get_all_battleship(self, color):
        battleship = []
        for row in self.board:
            for piece in row:
                if isinstance(piece, (Battleship)) and piece.color == color:
                    battleship.append(piece)
        return battleship

    def find_closest_enemy_battleship(self, piece):
        if piece.color == "White":
            return self.find_closest_black_battleship(piece)
        else:
            return self.find_closest_white_battleship(piece)

    def find_closest_black_battleship(self, piece):
        dist = 8
        curpiece = None
        for bs in self.black_battleship:
            curdist = max(abs(bs.row - piece.row), abs(bs.col - piece.col))
            if curdist < dist:
                dist = curdist
                curpiece = bs
        return curpiece

    def find_closest_white_battleship(self, piece):
        dist = 8
        curpiece = None
        for bs in self.white_battleship:
            curdist = max(abs(bs.row - piece.row), abs(bs.col - piece.col))
            if curdist < dist:
                dist = curdist
                curpiece = bs
        return curpiece

    # ---------------------------------------------------------
    # SAVE BOARD TO JSON
    # ---------------------------------------------------------
    def save_to_json(self, filepath):
        """
        Saves the board state to a JSON file.
        Only JSON‑safe data is stored (no Python objects).
        """

        data = {
            "pieces": []
        }

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece:
                    data["pieces"].append({
                        "type": piece.type,
                        "color": piece.color,
                        "row": piece.row,
                        "col": piece.col
                    })

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)


    # ---------------------------------------------------------
    # LOAD BOARD FROM JSON
    # ---------------------------------------------------------
    def load_from_json(self, filepath):
        """
        Loads a board state from a JSON file.
        Recreates all piece objects and places them on the board.
        """

        # Clear board
        self.board = [[0 for _ in range(8)] for _ in range(8)]

        with open(filepath, "r") as f:
            data = json.load(f)

        for p in data["pieces"]:
            piece_type = p["type"]
            color = p["color"]
            row = p["row"]
            col = p["col"]

            cls = PIECE_CLASS_MAP[piece_type]
            piece = cls(row, col, color)

            self.board[row][col] = piece

        # Rebuild caches
        self.find_all_torpedo()
        self.find_all_battleship()

    def save_to_dict(self):
        """Return a JSON‑serializable dict representing the board."""
        pieces = []

        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    pieces.append({
                        "type": p.type,
                        "color": p.color,
                        "row": p.row,
                        "col": p.col
                    })

        return {"pieces": pieces}

    def load_from_dict(self, data):
        """Load board state from a dict."""
        self.board = [[0 for _ in range(8)] for _ in range(8)]

        for p in data["pieces"]:
            cls = PIECE_CLASS_MAP[p["type"]]
            piece = cls(p["row"], p["col"], p["color"])
            self.board[p["row"]][p["col"]] = piece

        self.find_all_torpedo()
        self.find_all_battleship()