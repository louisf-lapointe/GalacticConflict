import sys
import json
from test.test_suites_runner import run_test_suite
from game.UserInterface import MainMenu
from game.game import Game
from game.board import Board
from game.move_history import MoveHistory


def main():
    # If user passed arguments, check for test mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run-tests":
            if len(sys.argv) < 3:
                print("Error: Missing test suite JSON file.")
                return
            test_json_path = sys.argv[2]
            run_test_suite(test_json_path)
            return

    # Default: run the UI
    MainMenu()


if __name__ == "__main__":
    main()
