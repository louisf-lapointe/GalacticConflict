import json
from game.game import Game
from game.board import Board
from game.move import Move
from game.move_history import MoveHistory


def load_game_from_position(json_path):
    """Load a Game object from a saved JSON position."""
    with open(json_path, "r") as f:
        data = json.load(f)

    # Create a new Game object
    game = Game(window=None, player_color=data["player_color"], theme=None)

    # Load board
    game.board.load_from_dict(data["board"])

    # Load move history
    game.move_history = MoveHistory()
    game.move_history.move_log = data["move_history"]

    # Load flags
    flags = data["flags"]
    game.battleship_eliminated_win = flags["battleship_eliminated_win"]
    game.no_move_loss = flags["no_move_loss"]
    game.dead_position_draw = flags["dead_position_draw"]
    game.threefold_draw = flags["threefold_draw"]
    game.no_captures_150 = flags["no_captures_150"]
    game.resign = flags["resign"]

    game.turn = data["turn"]

    game.computer.color = data["player_color"]

    return game


def run_ai_test(position_file, depth, expected_move):
    """Run a single AI test and return PASS/FAIL."""
    game = load_game_from_position(position_file)

    # Run minimax
    score, move = game.computer.minimax(
        game.board,
        game,
        depth,
        float("-inf"),
        float("inf"),
        game.computer.color
    )

    if move is None:
        return False, "AI returned no move"

    move_str = str(move)

    if move_str == expected_move:
        return True, f"PASS: {move_str}"
    else:
        return False, f"FAIL: expected {expected_move}, got {move_str}"


def run_test_suite(test_json_path):
    """Run all tests in the JSON test suite."""
    with open(test_json_path, "r") as f:
        tests = json.load(f)["tests"]

    print("Running AI Test Suite...\n")

    for t in tests:
        position_file = t["position_file"]
        depth = t["depth"]
        expected = t["expected_move"]

        ok, msg = run_ai_test(position_file, depth, expected)
        print(f"Test: {position_file} | Depth {depth}")
        print(msg)
        print("-" * 40)


