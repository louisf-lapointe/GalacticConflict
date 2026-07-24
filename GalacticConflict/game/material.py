import pygame

from pieces.fighter import Fighter
from pieces.corvette import Corvette
from pieces.interceptor import Interceptor
from pieces.bomber import Bomber
from pieces.dreadnought import Dreadnought
from pieces.battleship import Battleship
from pieces.torpedo import Torpedo

pygame.font.init()
my_font = pygame.font.SysFont("calibri", 15)


class Material(object):
    def __init__(self):
        self.black_advantage = 0
        self.white_advantage = 0
        self.captured_black_pieces = []
        self.captured_white_pieces = []

    # ---------------------------------------------------------
    # IMAGE LOOKUP
    # ---------------------------------------------------------

    def get_image(self, piece, color_index):
        image_map = {
            Fighter: Fighter.images[color_index],
            Corvette: Corvette.images[color_index],
            Interceptor: Interceptor.images[color_index],
            Bomber: Bomber.images[color_index],
            Dreadnought: Dreadnought.images[color_index],
            Battleship: Battleship.images[color_index],
            Torpedo: Torpedo.images[color_index],
        }

        image = image_map.get(type(piece))
        return pygame.transform.scale(image, (32, 32)) if image else None

    # ---------------------------------------------------------
    # DRAW CAPTURED PIECES
    # ---------------------------------------------------------

    def draw_captured(self, window, color):
        """
        Draw captured pieces for the UI.
        Layout is preserved from the chess version.
        """

        positions = {
            "White": [(480, 410, 25, 0), (480, 435, 25, -8)],
            "Black": [(480, 35, 25, 0), (480, 55, 25, -8)]
        }

        # Draw captured Black pieces (White captured them)
        color_index = 1
        for idx, piece in enumerate(self.captured_black_pieces):
            image = self.get_image(piece, color_index)
            if image:
                x_offset, y_base, spacing, shift = positions[color][0 if idx < 8 else 1]
                window.blit(image, (x_offset + (idx + shift) * spacing, y_base))

        # Draw captured White pieces (Black captured them)
        color_index = 0
        for idx, piece in enumerate(self.captured_white_pieces):
            image = self.get_image(piece, color_index)
            if image:
                x_offset, y_base, spacing, shift = positions[color][0 if idx < 8 else 1]
                window.blit(
                    image,
                    (x_offset + (idx + shift) * spacing,
                     y_base - 385 if color == "White" else 375)
                )

    # ---------------------------------------------------------
    # DRAW MATERIAL ADVANTAGE
    # ---------------------------------------------------------

    def draw_advantages(self, window, color):
        """
        Draw +X advantage next to captured pieces.
        """

        def draw_text(pieces_list, advantage, y_offsets):
            text = my_font.render(f"+{advantage}", True, (0, 0, 0))
            pieces_list.append(text)

            for piece in range(len(pieces_list)):
                if not isinstance(
                    pieces_list[piece],
                    (Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo)
                ):
                    x_offset = 460 + (piece + 1) * 25
                    y_offset = y_offsets[0] if piece <= 8 else y_offsets[1]
                    window.blit(pieces_list[piece], (x_offset, y_offset))
                    pieces_list.pop(-1)

        if self.white_advantage > self.black_advantage:
            draw_text(
                self.captured_black_pieces,
                self.white_advantage,
                (420 if color == "White" else 45,
                 445 if color == "White" else 70)
            )

        elif self.black_advantage > self.white_advantage:
            draw_text(
                self.captured_white_pieces,
                self.black_advantage,
                (35 if color == "White" else 410,
                 60 if color == "White" else 435)
            )

    # ---------------------------------------------------------
    # MATERIAL CALCULATION
    # ---------------------------------------------------------

    def update_advantages(self, board):
        """
        Galactic Conflict material values:
        - Fighter: 1
        - Corvette: 3
        - Interceptor: 4
        - Bomber: 5
        - Dreadnought: 9
        - Battleship: infinite (but we treat as 10 for material)
        - Torpedo: 2 (but non-strategic)
        """

        value_map = {
            Fighter: 1,
            Corvette: 3,
            Interceptor: 4,
            Bomber: 5,
            Dreadnought: 9,
            Battleship: 10,
            Torpedo: 2
        }

        black_adv, white_adv = 0, 0

        for row in board.board:
            for piece in row:
                if type(piece) in value_map:
                    if piece.color == "White":
                        white_adv += value_map[type(piece)]
                    else:
                        black_adv += value_map[type(piece)]

        self.white_advantage = max(0, white_adv - black_adv)
        self.black_advantage = max(0, black_adv - white_adv)

    # ---------------------------------------------------------
    # CAPTURE LIST SORTING
    # ---------------------------------------------------------

    def add_to_captured_pieces(self, piece, capture_list):
        """
        Sort captured pieces by material value.
        """

        priority = [
            Fighter, Corvette, Interceptor, Bomber, Dreadnought, Battleship, Torpedo
        ]

        piece_priority = priority.index(type(piece))

        for i, curr in enumerate(capture_list):
            if priority.index(type(curr)) > piece_priority:
                capture_list.insert(i, piece)
                return

        capture_list.append(piece)