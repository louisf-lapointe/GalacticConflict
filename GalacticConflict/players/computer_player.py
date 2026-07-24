import copy
from queue import Empty
import random
import pygame
from game.profiler import Profiler
from game.half_turn import HalfTurn
from game.move_transform import MoveTransform

from pieces import fighter, corvette, interceptor, bomber, dreadnought, battleship, torpedo
from pieces.fighter import Fighter
from pieces.corvette import Corvette
from pieces.interceptor import Interceptor
from pieces.bomber import Bomber
from pieces.dreadnought import Dreadnought
from pieces.battleship import Battleship
from pieces.torpedo import Torpedo


class Computer(object):
  WHITE = "White"
  BLACK = "Black"

  PIECE_TYPES = (Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo)
  PIECE_EVALUATION_TABLES = {
    (WHITE, "Fighter"): (100, fighter.white_fighter_eval_table),
    (WHITE, "Corvette"): (300, corvette.white_corvette_eval_table),
    (WHITE, "Interceptor"): (400, interceptor.white_interceptor_eval_table),
    (WHITE, "Bomber"): (500, bomber.white_bomber_eval_table),
    (WHITE, "Dreadnought"): (900, dreadnought.white_dreadnought_eval_table),
    (WHITE, "Battleship"): (1000, battleship.white_battleship_eval_table),
    (WHITE, "Torpedo"): (200, torpedo.white_torpedo_eval_table),

    (BLACK, "Fighter"): (100, fighter.black_fighter_eval_table),
    (BLACK, "Corvette"): (300, corvette.black_corvette_eval_table),
    (BLACK, "Interceptor"): (400, interceptor.black_interceptor_eval_table),
    (BLACK, "Bomber"): (500, bomber.black_bomber_eval_table),
    (BLACK, "Dreadnought"): (900, dreadnought.black_dreadnought_eval_table),
    (BLACK, "Battleship"): (1000, battleship.black_battleship_eval_table),
    (BLACK, "Torpedo"): (200, torpedo.black_torpedo_eval_table),
  }

  def __init__(self, color):
    self.profiler = Profiler()
    self.color = color
    self.transposition_table = {}
    self.piece_value_cache = {}

    # These values provide the user valuable information about the current state of the minimax search
    self.moves_evaluated = 0
    self.total_moves_found = 0
    self.current_best_evaluation = 0

  def minimax(self, board, game, depth, alpha, beta, max_player):
        """
        Implements the Minimax algorithm to calculate the move that would maximize the AI's positional evaluation.
        Includes alpha-beta pruning to reduce the size of the search tree and reduce redundant computations.
        """
        if depth == 0 or game.game_over():
            return self.evaluate_board(board, max_player), None

        if max_player == self.WHITE and len(board.black_battleship) == 0:
            return float("inf"), board
        elif max_player == self.BLACK and len(board.white_battleship) == 0:
            return float("-inf"), board
            

        best_score = float("-inf") if max_player == self.WHITE else float("inf")
        other_player = self.BLACK if max_player == self.WHITE else self.WHITE

        all_moves = self.get_all_moves(board, game, max_player)
        if len(all_moves) == 0:
            if max_player == self.WHITE:
                return float("-inf"), None
            else:
                return float("inf"), None
        best_move = all_moves[0]
        self.total_moves_found += len(all_moves)

        for move in all_moves:
            position = self.simulate_move(board, game, move, max_player)
            self.draw_AI_calculations(game, move, position)
            current_score, _ = self.minimax(position, game, depth - 1, alpha, beta, other_player)
            board.undo_move()

            if max_player == self.WHITE:
                if current_score > best_score:
                    best_score = current_score
                    best_move = move
                    alpha = max(alpha, best_score)

            if max_player == self.BLACK:
                if current_score < best_score:
                    best_score = current_score
                    best_move = move
                    beta = min(beta, best_score)

            self.current_best_evaluation = best_score

            # if beta <= alpha, it means that the maximizing player already has a move with a better outcome than the current branch's best possible outcome
            # this means that we can can prune this branch to reduce unneccessary computations since we know that the maximizing player will never choose this branch
            # ASIDE: alpha-beta pruning assumes that both players are making optimal moves to maximize or minimize their respective scores
            if beta <= alpha:
                break

        return best_score, best_move

  def minimax_debug(self, board, game, depth, alpha, beta, max_player):
        previous_move = None
        if depth == 0 or game.game_over():
            return self.evaluate_board(board, max_player), None, previous_move

        if max_player == self.WHITE and len(board.black_battleship) == 0:
            return float("inf"), board, previous_move
        elif max_player == self.BLACK and len(board.white_battleship) ==0:
            return float("-inf"), board, previous_move
            
        best_score = float("-inf") if max_player == self.WHITE else float("inf")
        other_player = self.BLACK if max_player == self.WHITE else self.WHITE

        all_moves = self.get_all_moves(board, game, max_player)
        if len(all_moves) == 0:
            if max_player == self.WHITE:
                return float("-inf"), None, previous_move
            else:
                return float("inf"), None, previous_move
        best_move = all_moves[0]
        self.total_moves_found += len(all_moves)

        for move in all_moves:
            position = self.simulate_move(board, game, move, max_player)
            self.draw_AI_calculations(game, move, position)
            current_score, _, deep_move = self.minimax_debug(position, game, depth - 1, alpha, beta, other_player)
            board.undo_move()

            if max_player == self.WHITE:
                if current_score > best_score:
                    best_score = current_score
                    best_move = move
                    alpha = max(alpha, best_score)
                    if deep_move is None:
                        previous_move = best_move
                    else:
                        if depth == 2:
                            previous_move = best_move
                        else:
                            previous_move = deep_move

            if max_player == self.BLACK:
                if current_score < best_score:
                    best_score = current_score
                    best_move = move
                    beta = min(beta, best_score)
                    if deep_move is None:
                        previous_move = best_move
                    else:
                        if depth == 2:
                            previous_move = best_move
                        else:
                            previous_move = deep_move

            self.current_best_evaluation = best_score

            if beta <= alpha:
                break

        if depth == 3:
            print(f"Score: {best_score}, Move {best_move}, Previous move {previous_move}")
        return best_score, best_move, previous_move

  def get_piece_value(self, piece):
    """
    Calculate the value of a piece using material and positional evaluation.
    """
    piece_key = (piece.color, piece.type, piece.row, piece.col)
    if piece_key in self.piece_value_cache:
        return self.piece_value_cache[piece_key]

    piece_material, piece_eval_table = self.PIECE_EVALUATION_TABLES[(piece_key[0], piece_key[1])]
    piece_index = (piece.row * 8) + piece.col
    piece_value = piece_material + piece_eval_table[piece_index]

    # cache this for future lookups
    self.piece_value_cache[piece_key] = piece_value
    return piece_value

  @Profiler.profile_function
  def evaluate_board(self, board, max_player):
    """
    Evaluate the board state, considering material and positional advantages.
    """
    if max_player[0] == 'W':
        if len(board.black_battleship) == 0:
            return float("inf")
        elif len(board.white_battleship) == 0:
            return float("-inf")
    else:
        if len(board.white_battleship) == 0:
            return float("-inf")
        elif len(board.black_battleship) == 0:
            return float("inf")

    position_eval = 0
    for row in board.board:
        for piece in row:
            if not piece:
                continue

            piece_key = (piece.color, piece.type, piece.row, piece.col)
            if piece_key not in self.piece_value_cache:
                self.piece_value_cache[piece_key] = self.get_piece_value(piece)

            if piece.color == self.BLACK:
                position_eval -= self.piece_value_cache[piece_key]
            else:
                position_eval += self.piece_value_cache[piece_key]

    return position_eval

  @Profiler.profile_function
  def get_all_moves(self, board, game, color):
    """
    Generates all possible moves for each piece that the player owns.
    """
    all_moves = []
    passive_moves = []
    moves_with_capture = []

    for piece in board.get_all_pieces(color):
        piece.update_valid_moves(board.board)

        for amove in piece.valid_moves:
            row = amove.row()
            col = amove.col()
            if board.board[row][col] != 0 and board.get_piece(row, col).color != color:
                moves_with_capture.append(((piece.row, piece.col), (row, col)))
            else:
                passive_moves.append(((piece.row, piece.col), (row, col)))

    moves_with_capture = self.order_moves(moves_with_capture, board.board)

    # by using move ordering and putting moves where the AI captured a piece first, we evaluate the moves
    # that are likely to be the strongest earlier in the search tree, making alpha-beta pruning more efficient.
    all_moves.extend(moves_with_capture)
    all_moves.extend(passive_moves)
    return all_moves

  @Profiler.profile_function
  def order_moves(self, moves, board):
    def mvv_lva(move):  # https://www.chessprogramming.org/MVV-LVA
        (startRow, startCol), (targetRow, targetCol) = move
        piece = board[startRow][startCol]

        piece_key = (piece.color, piece.type, piece.row, piece.col)
        if piece_key not in self.piece_value_cache:
            self.piece_value_cache[piece_key] = self.get_piece_value(piece)
      
        target = board[targetRow][targetCol]
        target_key = (target.color, target.type, target.row, target.col)
        if target_key not in self.piece_value_cache:
            self.piece_value_cache[target_key] = self.get_piece_value(target)

        return self.piece_value_cache[target_key] - self.piece_value_cache[piece_key]

    return sorted(moves, key=mvv_lva, reverse=True)

  def draw_AI_calculations(self, game, move, board):
    """
    If the user has enabled the visualize AI feature, show the current position that the AI is considering after every move.
    """
    self.moves_evaluated += 1

    if not game.board.show_AI_calculations:
        return

    if game.board.AI_speed == "Medium":
        pygame.time.delay(20)
    elif game.board.AI_speed == "Slow":
        pygame.time.delay(50)

    self.draw_moves(move, game, board)

  @Profiler.profile_function
  def simulate_move(self, board, game, start_end_move, color):
    """
    Simulates a move on the board.
    """
    start_move, end_move = start_end_move
    target = board.get_piece(end_move[0], end_move[1])

    board.prev_square = (start_move[0], start_move[1])
    board.piece = board.board[start_move[0]][start_move[1]]
    board.target = (end_move[0], end_move[1])

    ht_obj = board.move(start_move[0], start_move[1], end_move[0], end_move[1])

    board.stored_moves.append(ht_obj)

    return board

  def draw_moves(self, move, game, board):
    (srow, scol), (erow, ecol) = move
    piece = board.get_piece(srow, scol)
    if piece != 0:
        valid_moves = piece.valid_moves
        game.update_screen(valid_moves, board)
    epiece = board.get_piece(erow, ecol)
    if epiece != 0:
        valid_moves = epiece.valid_moves
        game.update_screen(valid_moves, board)


  def computer_move(self, game, move):
    """
    move = (piece, (row, col))
    This function:
    - Simulates the move
    - Applies special GC rules
    - Builds proper GC notation using Move class
    - Updates the game state
    """
    if move is None:
        return

    (prev_row, prev_col), (row, col) = move
    board_obj = game.board

    target_piece = board_obj.get_piece(row, col)
    piece = board_obj.get_piece(prev_row, prev_col)
    is_capture = target_piece != 0 and target_piece.color != piece.color

    # ---------------------------------------------------------
    # CAPTURE
    # ---------------------------------------------------------
    if is_capture:
        game.capture(target_piece)


    # ---------------------------------------------------------
    # MOVE THE PIECE
    # ---------------------------------------------------------
    before_type = piece.type
    ht_obj = board_obj.move(prev_row, prev_col, row, col)

    notation = str(ht_obj)

    # ---------------------------------------------------------
    # UPDATE GAME STATE
    # ---------------------------------------------------------
    game.move_history.move_log.append(notation)
    board_obj.previous_move = ht_obj

    game.update_game()
    game.check_game_status()

    # Profiling (if you still use it)
    self.profiler.print_profile_summary(self.moves_evaluated)
    self.profiler.reset_profiler()