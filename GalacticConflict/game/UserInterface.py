import tkinter as tk
from PIL import Image, ImageTk
import pygame
from game.constants import width, height, square_size, themes
from game.game import Game
import threading
import traceback


def position_window(root):
  root.minsize(400, 240)
  w = 400  # width of the window
  h = 240  # height of the window

  ws = root.winfo_screenwidth()  # width of the screen
  hs = root.winfo_screenheight()  # height of the screen

  # calculate x and y coordinates for the window
  x = (ws / 2) - (w / 2)
  y = (hs / 2) - (h / 2)

  # set the dimensions of the screen and where it is placed
  root.geometry('%dx%d+%d+%d' % (w, h, x, y))


class MainMenu(object):
  def __init__(self):
    self.root = tk.Tk()
    self.root.title("Galactic Conflict")
    position_window(self.root)
    self.create_window()
    self.root.mainloop()

  def create_window(self):
    single_frame = tk.Frame(self.root, bg="lightskyblue")
    multi_frame = tk.Frame(self.root, bg="salmon1")
    single_frame.grid(row=0, column=0, sticky="nsew")
    multi_frame.grid(row=0, column=1, sticky="nsew")
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.root.columnconfigure(1, weight=1)

    single_player = tk.Button(self.root, text="Single Player", command=self.single_player)
    single_player.place(x=50, y=100, height=40, width=100)

    local_multiplayer = tk.Button(self.root, text="Local Multiplayer", command=self.multiplayer)
    local_multiplayer.place(x=250, y=100, height=40, width=100)

  def single_player(self):
    self.root.destroy()
    SinglePlayer()

  def multiplayer(self):
    self.root.destroy()
    Multiplayer()


class SinglePlayer(object):
  def __init__(self):
    self.root = tk.Tk()
    self.root.configure(background="lightskyblue")
    self.root.title = "Single Player Chess"
    position_window(self.root)
    self.white_king_image = ImageTk.PhotoImage(Image.open("pieces/assets/White_Battleship.png"))
    self.black_king_image = ImageTk.PhotoImage(Image.open("pieces/assets/Black_Battleship.png"))
    self.difficulty = tk.StringVar(self.root)
    self.color = ""
    self.create_window()
    self.root.mainloop()

  def create_window(self):
    main_menu = tk.Button(self.root, text="Main Menu", command=self.main_menu)
    main_menu.place(x=150, y=20, height=40, width=100)

    difficulties = [("Easy", "(Depth-2)"), ("Medium", "(Depth-3)"), ("Hard", "(Depth-4)"),
                    ("Veteran", "(Depth-5)"), ("Expert", "(Depth-6)")]
    difficulty_selection = tk.OptionMenu(self.root, self.difficulty, *difficulties)
    difficulty_selection.place(x=130, y=80, height=32, width=140)

    if self.color == "":
      white_king = tk.Button(self.root, bg="lightskyblue", image=self.white_king_image,
                             command=lambda color="White": self.select_color(color))
      black_king = tk.Button(self.root, bg="lightskyblue", image=self.black_king_image,
                             command=lambda color="Black": self.select_color(color))

    elif self.color == "White":
      white_king = tk.Button(self.root, bg="salmon", image=self.white_king_image,
                             command=lambda color="White": self.select_color(color))
      black_king = tk.Button(self.root, bg="lightskyblue", image=self.black_king_image,
                             command=lambda color="Black": self.select_color(color))

    else:
      white_king = tk.Button(self.root, bg="lightskyblue", image=self.white_king_image,
                             command=lambda color="White": self.select_color(color))
      black_king = tk.Button(self.root, bg="salmon", image=self.black_king_image,
                             command=lambda color="Black": self.select_color(color))

    white_king.place(x=60, y=80, height=64, width=64)
    black_king.place(x=275, y=80, height=64, width=64)

    play = tk.Button(self.root, text="Play", command=self.play)
    play.place(x=150, y=140, height=40, width=100)

  def select_color(self, color):
    self.color = color
    self.create_window()
    self.root.update()

  def main_menu(self):
    self.root.destroy()
    MainMenu()

  def play(self):
    if self.color != "" and self.difficulty != "PY_VAR0":
      difficulty = self.difficulty.get()

      if "Easy" in difficulty:
        single_player_game(self.color, 0, 2)
        self.root.destroy()

      elif "Medium" in difficulty:
        single_player_game(self.color, 0, 3)
        self.root.destroy()

      elif "Hard" in difficulty:
        single_player_game(self.color, 0, 4)
        self.root.destroy()

      elif "Veteran" in difficulty:
        single_player_game(self.color, 0, 5)
        self.root.destroy()

      elif "Expert" in difficulty:
        single_player_game(self.color, 0, 6)
        self.root.destroy()


class Multiplayer(object):
  def __init__(self):
    self.root = tk.Tk()
    self.root.configure(background="salmon1")
    self.root.title = "Multi Player Chess"
    position_window(self.root)
    self.create_window()
    self.root.mainloop()

  def create_window(self):
    main_menu = tk.Button(self.root, text="Main Menu", command=self.main_menu)
    main_menu.place(x=150, y=70, height=40, width=100)

    play = tk.Button(self.root, text="Play", command=self.play)
    play.place(x=150, y=130, height=40, width=100)

  def main_menu(self):
    self.root.destroy()
    MainMenu()

  def play(self):
    multiplayer_game("White", 0)
    self.root.destroy()


pygame.font.init()
my_font = pygame.font.SysFont("calibri", 15)
letters = ["a", "b", "c", "d", "e", "f", "g", "h"]


def calc_mouse_pos(pos, color):
  if color == "White":
      row = pos[1] // square_size
      col = pos[0] // square_size
  else:
      row = 7 - pos[1] // square_size
      col = 7 - pos[0] // square_size
  return row, col


def multiplayer_game(color, theme):
  pygame.init()
  game_window = pygame.display.set_mode((width, height))
  pygame.display.set_caption("Galactic Conflict By Louis-Francois Lapointe")
  gc_game = Game(game_window, color, theme)
  gc_game.board.initiate_pieces()
  fps = 60
  clock = pygame.time.Clock()
  running = True
  while running:
    clock.tick(fps)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_xy = pygame.mouse.get_pos()
        row, col = calc_mouse_pos(mouse_xy, color)
        if gc_game.game_over():
          if 117 <= mouse_xy[0] <= 223 and 217 <= mouse_xy[1] <= 273:
            if color == "White":
              multiplayer_game("Black", gc_game.theme)
            else:
              multiplayer_game("White", gc_game.theme)
          elif 247 <= mouse_xy[0] <= 353 and 217 <= mouse_xy[1] <= 273:
            running = False
        else:
          gc_game.human.select(row, col, mouse_xy)

    if gc_game.game_over():
      draw_end_screen(gc_game, game_window)
    else:
      gc_game.update_screen(gc_game.human.valid_moves, gc_game.board)

  pygame.quit()


def single_player_game(color, theme, depth):
  pygame.init()
  game_window = pygame.display.set_mode((width, height))
  pygame.display.set_caption(f"Galactic Conflict by Louis-Francois Lapointe")
  gc_game = Game(game_window, color, theme)
  gc_game.board.initiate_pieces()
  fps = 120
  clock = pygame.time.Clock()
  running = True
  ai_thinking = False
  
  # Function to handle AI move generation in a separate thread
  def multithread_minimax():
    try:
        nonlocal ai_thinking  # Access the ai_thinking flag
        debug_minimax = False
        if debug_minimax:
            _, move, _ = gc_game.computer.minimax_debug(gc_game.board, gc_game, depth,
                                          float("-inf"), float("inf"), gc_game.computer.color)
        else:
            _, move = gc_game.computer.minimax(gc_game.board, gc_game, depth,
                                          float("-inf"), float("inf"), gc_game.computer.color)
        if move == None:
            gc_game.check_game_status()
        else:
            gc_game.computer.computer_move(gc_game, move)

        ai_thinking = False  # Reset the flag once AI has made its move
    except ValueError:
        # Prints the full call stack to stderr
        traceback.print_exc()    
        
  while running:
    clock.tick(fps)
    for event in pygame.event.get():      
      if event.type == pygame.QUIT:
        running = False

      if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_xy = pygame.mouse.get_pos()
        row, col = calc_mouse_pos(mouse_xy, color)
        if gc_game.game_over():
          if 117 <= mouse_xy[0] <= 223 and 217 <= mouse_xy[1] <= 273:
            if color == "White":
              single_player_game("Black", gc_game.theme, depth)
            else:
              single_player_game("White", gc_game.theme, depth)
          elif 247 <= mouse_xy[0] <= 353 and 217 <= mouse_xy[1] <= 273:
            running = False
        else:
          gc_game.human.select(row, col, mouse_xy, ai_thinking)

    if gc_game.turn == gc_game.computer.color and not gc_game.game_over():
      if not ai_thinking: 
        ai_thinking = True
        threading.Thread(target=multithread_minimax).start()

    # If AI is thinking, freeze the screen
    if ai_thinking:
      continue
    
    if gc_game.game_over():
      draw_end_screen(gc_game, game_window)
    else:
      gc_game.update_screen(gc_game.human.valid_moves, gc_game.board)

  pygame.quit()


def draw_end_screen(gc_game, game_window):
  if gc_game.battleship_eliminated_win:
    if gc_game.turn == "White":
      main_text = my_font.render("White won by eliminating battleships.", True, [0, 0, 0])
    else:
      main_text = my_font.render("Black won by eliminating battleships.", True, [0, 0, 0])
  elif gc_game.no_move_loss:
    if gc_game.turn == "White":
      main_text = my_font.render("Black won by restricting White pieces.", True, [0, 0, 0])
    else:
      main_text = my_font.render("White won by restricting Black pieces.", True, [0, 0, 0])
  elif gc_game.threefold_draw:
    main_text = my_font.render("Draw by threefold repetition.", True, [0, 0, 0])
  elif gc_game.resign:
    main_text = my_font.render(gc_game.turn + " has resigned the game.", True, [0, 0, 0])
  else:
    main_text = my_font.render("Draw by insufficient material.", True, [0, 0, 0])

  # The main box, border, and text
  pygame.draw.rect(game_window, [0, 0, 0], (85, 160, 310, 160))
  pygame.draw.rect(game_window, [255, 255, 255], (87, 162, 306, 156))
  game_window.blit(main_text, (150, 180))

  # Play again button
  pygame.draw.rect(game_window, [0, 0, 0], (115, 215, 110, 60))
  pygame.draw.rect(game_window, themes[gc_game.theme][1], (117, 217, 106, 56))
  play_again_text = my_font.render("Play Again", True, [0, 0, 0])
  game_window.blit(play_again_text, (140, 235))

  # Quit button
  pygame.draw.rect(game_window, [0, 0, 0], (245, 215, 110, 60))
  pygame.draw.rect(game_window, themes[gc_game.theme][1], (247, 217, 106, 56))
  quit_text = my_font.render("Quit", True, [0, 0, 0])
  game_window.blit(quit_text, (285, 235))

  pygame.display.update()


if __name__ == "__main__":
  MainMenu()
