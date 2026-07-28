# Galactic Conflict by Louis-Francois Lapointe based on a project from Jeffery Xie
A functional chess variant game implemented in Python, with pygame as a supporting module. This program includes single-player vs an AI, which uses the minimax algorithm to determine its moves. A special feature of this program is the "visual" aspect, where the user can toggle a setting that allows them to see which moves the computer is currently considering in real time.

# Table of Contents
* [Demo Images](#demo)
* [Notes to User](#notes)
* [Features](#features)
* [Implemented Game Mechanics](#mechanics)
* [Requirements and Installation](#req)
* [Future Implementations](#future)
* [Known Bugs](#bugs)
* [Extra Information](#extra)

# Notes to User <a name="notes"></a>
* Note that Pygame's graphics are going to be different depending on the machine/version of machine that you are using.
* **AI Difficulties Guidelines**
  * Note that the search time for moves depends on search depth, as the number of moves to evaluate increases exponentially with the depth.
  * Depth is how many moves the AI will look ahead when computing its move. For example, a depth of 3 means that the AI will look 3 moves ahead.
  * Any depth lower than hard (Depth 4) should move nearly instantly on most machines.

# Features <a name="features"></a>
* Single Player vs AI
  * AI implements the minimax algorithm to determine its moves.
    * To optimize the minimax algorithm, Jeffery also implemented alpha-beta pruning to cut branches off early when they are worse than a move that has already been seen.
  * The evaluation function for the algorithm is based on pre-determined piece values and piece square tables (how much a piece is worth, plus the relative strength of the piece in respect to its position on the board).
  * A togglable feature that shows the AI thinking in real time, displaying all board outcomes from the possible moves.
    * It also includes three speeds for this if the display is moving too fast (slow, medium, fast).
* A move history log with a new standard notation.
* Tile indicators that show available moves for the piece that you have selected (toggleable).
  * Also shows the previous move that was made.
* Variety of chess board themes to choose from.
* Material tracker that displays captured pieces and advantages.
* Louis-Francois added a save and load that modifies the /save/save.json
  
# Implemented Game Mechanics <a name="mechanics"></a>
* Promotion and demotions.
* Invalid move prevention.
* Draw by insufficient material.
* Draw by 150 moves, no captures.

# Requirements and Installation <a name="req"></a>
Make sure you have a Python version of 3.x or higher!

**Required Modules**

To install it, simply enter these commands into your terminal. (for macOS users, replace pip with pip3)
* For help with installing pip: visit https://pip.pypa.io/en/stable/installing/
* *pip install pygame*
  * If the command above does not work, visit https://www.pygame.org/wiki/GettingStarted for help.
* *py -3.13 -m pip install -U pygame --user*
* *py -3.13 -m pip install -U Pillow --user*
* *pip install tkinter*

**Setting up Repository**
* To clone the repository, press the green "Code" button and copy the HTTPS to your clipboard.
* Create a new project in your code editor or IDE of choice.
* Import the HTTPS url into version control on your new project.
* Two Examples:
  * If using pycharm, go to VCS --> get from version control --> paste the url --> clone
  * If using Visual Studio Code, go to explorer (ctrl + shift + e) --> clone repository --> paste the url --> clone

**Running**
* Running the galacticconflict.py file will start the program!

# Future Implementations <a name="future"></a>
* Implement Human-Human and Computer-Computer game
* In Human-Human, implement an Undo Move button
* Optimize the inputs of the evaluations based on ever optimizing algorithm when Computer-Computer play infinite games.
*   Inputs are currently piece value and positional bonus
* Using more threads to dispatch evaluations at the first depth level only.
* A 3-7 man database for all the possible endings.

# Known Bugs <a name="bugs"></a>
* Color of the top-left diagonal is wrong. That gives a wrong color for the Dreadnought. This could be a feature for this vairant?

# Extra Information <a name="extra"></a>
The AI can hold its own against a casual player but has no grasp of positional concepts or mid to late-game tactics/evaluations. The strength of the AI depends on the strength and complexity of the evaluation function, which is currently a very simple evaluation. It calculates the material still left on the board (pieces) and then calculates the relative strength of each piece based on its position on the board using piece-square tables.
* To learn more, visit https://www.chessprogramming.org/Simplified_Evaluation_Function

*Nice Visual Feature*
* You can turn on a visualizer to see the AI calculating its move in real time. This feature will slow the AI down a lot, so it is not recommended to play a full game with this feature on; it should be used to visually learn how the minimax algorithm works.

*Minimax Algorithm*
* In zero-sum games such as chess and checkers, where one player winning means that the other player has to lose, the minimax algorithm can be used to create an AI. The minimax algorithm calculates the relative strength of each player on the board and returns a number based on its evaluation function. The min player (black in chess) makes moves that will make the evaluation of the current board as small as possible, and the max player (white in chess) will make moves that make the evaluation of the current board as big as possible. 
  * To learn more, visit https://www.chessprogramming.org/Minimax
* As you increase the depth, the AI will play better, at the cost of taking exponentially more time to calculate its best move.
  * At a depth of 1, the AI will look through all of its available moves for its pieces and calculate the best move that improves its current position without thinking about the future repercussions of its move. This means that if the AI is allowed to take a piece, it always will. (The AI will prioritize pieces with higher values, ex. Capturing Queen > Capturing Knight) 
  * At a depth of 2, the AI will calculate its current best move, along with calculating your best move if they make that particular move. Calculating the strength of the moves is where the minimax algorithm comes in. It tries to minimize the strength of your best response while also maximizing the strength of its move.
  * At a depth of 3, the AI can calculate its position after its current best move, calculate the position after your best move in response, and then assuming you make the best possible move (up to the standards of the eval function), it can also calculate its next best move and position.

*Alpha Beta Pruning*
* I also implemented alpha-beta pruning to optimize the minimax algorithm. The minimax algorithm is particularly slow when it comes to large games such as chess, because there are so many different moves and positions that can occur and the minimax algorithm needs to search through all of the moves. Alpha Beta Pruning keeps track of the best move seen so far, and will cut branches off early when it sees that the move that it is currently evaluating is worse than the current best move.
  * To learn more, visit https://www.chessprogramming.org/Alpha-Beta

Chess Assets were downloaded from this free media repository: https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent

[Algorithms Explained – minimax and alpha-beta pruning](https://www.youtube.com/watch?v=l-hh51ncgDI)
