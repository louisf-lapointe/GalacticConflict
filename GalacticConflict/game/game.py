import pygame
import json
from game.board import Board
from pieces.fighter import Fighter
from pieces.corvette import Corvette
from pieces.interceptor import Interceptor
from pieces.bomber import Bomber
from pieces.dreadnought import Dreadnought
from pieces.battleship import Battleship
from pieces.torpedo import Torpedo
from game.move_history import MoveHistory
from game.constants import themes
from players.human_player import Human
from players.computer_player import Computer


class Game(object):
    def __init__(self, window, player_color, theme):
        self.window = window
        self.theme = theme
        self.move_history = MoveHistory()
        self.human = Human(player_color, self)
        self.board = Board(player_color)
        self.computer = Computer("Black" if player_color == "White" else "White")
        self.turn = "White"

        # Game Over Conditions (adapted to Galactic Conflict)
        self.battleship_eliminated_win = False
        self.no_move_loss = False
        self.dead_position_draw = False
        self.threefold_draw = False
        self.no_captures_150 = False
        self.resign = False

    def game_over(self):
        return any([
            self.battleship_eliminated_win,
            self.no_move_loss,
            self.dead_position_draw,
            self.no_captures_150,
            self.resign
        ])

    def update_screen(self, valid_moves, board):
        self.board.create_board(self.window, themes[self.theme])
        self.board.draw_previous_move(self.window)

        if self.board.show_valid_moves:
            self.board.draw_valid_moves(valid_moves, self.window)

        self.board.draw_theme_window(self.window)
        self.board.draw_game_buttons(self.window, themes[self.theme], self.computer)

        self.move_history.draw_move_log(self.window)
        self.board.material.draw_captured(self.window, self.human.color)
        self.board.material.draw_advantages(self.window, self.human.color)

        self.board.draw(self.window, board)

        pygame.display.update()

    def update_game(self):
        self.board.material.update_advantages(self.board)
        self.change_turn()
        self.update_all_valid_moves()
        self.check_game_status()

    # ---------------------------------------------------------
    # STATUS / RULES
    # ---------------------------------------------------------

    def check_game_status(self):
        # Win if opponent has no Battleship
        if self.opponent_has_no_battleship():
            self.battleship_eliminated_win = True
            self.update_screen(self.human.valid_moves, self.board)
            return

        if self.has_no_move():
            self.no_move_loss = True
            self.update_screen(self.human.valid_moves, self.board)
            return

        # Draw conditions
        self.threefold_repetition()
        self.no_captures_in_150()
        self.dead_position()

    def opponent_has_no_battleship(self):
        opponent = "Black" if self.turn == "White" else "White"
        for row in self.board.board:
            for piece in row:
                if isinstance(piece, Battleship) and piece.color == opponent:
                    return False
        return True

    def has_no_move(self):
        for row in self.board.board:
            for piece in row:
                if piece != 0 and piece.color == self.turn:
                    if len(piece.update_valid_moves(self.board.board)) > 0:
                        return False
        return True

    def update_all_valid_moves(self):
        for row in self.board.board:
            for piece in row:
                if isinstance(
                    piece,
                    (Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo)
                ):
                    piece.update_valid_moves(self.board.board)

    def get_dangerous_squares(self):
        dangerous_squares = []
        for row in self.board.board:
            for piece in row:
                if isinstance(
                    piece,
                    (Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo)
                ):
                    if piece.color != self.turn:
                        dangerous_squares.extend(piece.valid_moves)
        return dangerous_squares

    def battleship_under_attack(self):
        self.update_all_valid_moves()
        dangerous_squares = self.get_dangerous_squares()
        battleship = None
        battleship_pos = (None, None)

        for row in self.board.board:
            for piece in row:
                if isinstance(piece, Battleship) and piece.color == self.turn:
                    battleship_pos = (piece.row, piece.col)
                    battleship = piece
                    break

        if battleship is None:
            # No Battleship for current side: they have already lost
            return True

        if battleship_pos in dangerous_squares:
            battleship.is_checked = True
            return True

        battleship.is_checked = False
        return False

    def dead_position(self):
        """
        Simple dead-position heuristic:
        - Conditions must be found by further game testing.
        """
        has_battleship = 0;
        has_other = False  # pieces that can (directly or indirectly) attack Battleships

        for row in self.board.board:
            for piece in row:
                if isinstance(piece, Battleship):
                    has_battleship += 1
                else:
                    has_other = True


        if has_battleship <= 2 and (not has_other):
            self.dead_position_draw = True
            self.update_screen(self.human.valid_moves, self.board)

    def threefold_repetition(self):
        unique_moves = set(self.move_history.move_log[-9:])
        if len(self.move_history.move_log) > 9 and len(unique_moves) == 4:
            self.update_screen(self.human.valid_moves, self.board)
            self.threefold_draw = True

    def no_captures_in_150(self):
        if len(self.move_history.move_log) > 150:
            moves = self.move_history.move_log[-150:]
            captures = [move for move in moves if "x" in move]
            if len(captures) == 0:
                self.no_captures_150 = True

    # ---------------------------------------------------------
    # TURN / MOVE HELPERS
    # ---------------------------------------------------------

    def change_turn(self):
        self.human.valid_moves = []
        self.turn = "Black" if self.turn == "White" else "White"

    def capture(self, piece):
        if piece.color == "Black":
            self.board.material.add_to_captured_pieces(
                piece, self.board.material.captured_black_pieces
            )
        else:
            self.board.material.add_to_captured_pieces(
                piece, self.board.material.captured_white_pieces
            )

    def save_to_json(self, filepath):
        """
        Save the entire game state to a JSON file.
        """

        data = {
            "player_color": self.human.color,
            "turn": self.turn,

            "board": self.board.save_to_dict(),

            "move_history": self.move_history.move_log,

            "flags": {
                "battleship_eliminated_win": self.battleship_eliminated_win,
                "no_move_loss": self.no_move_loss,
                "dead_position_draw": self.dead_position_draw,
                "threefold_draw": self.threefold_draw,
                "no_captures_150": self.no_captures_150,
                "resign": self.resign
            }
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self, filepath):
        """
        Load the entire game state from a JSON file.
        """

        with open(filepath, "r") as f:
            data = json.load(f)

        # Restore player color
        player_color = data["player_color"]

        # Rebuild Human + Computer
        self.human = Human(player_color, self)
        self.computer = Computer("Black" if player_color == "White" else "White")

        # Restore turn
        self.turn = data["turn"]

        # Restore board
        self.board = Board(player_color)
        self.board.load_from_dict(data["board"])

        # Restore move history
        self.move_history = MoveHistory()
        self.move_history.move_log = data["move_history"]

        # Restore flags
        flags = data["flags"]
        self.battleship_eliminated_win = flags["battleship_eliminated_win"]
        self.no_move_loss = flags["no_move_loss"]
        self.dead_position_draw = flags["dead_position_draw"]
        self.threefold_draw = flags["threefold_draw"]
        self.no_captures_150 = flags["no_captures_150"]
        self.resign = flags["resign"]

        # Rebuild screen
        self.update_screen([], self.board)
