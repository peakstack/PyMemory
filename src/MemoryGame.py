import itertools
import math
import random
from enum import Enum
from pathlib import Path

import pygame
import pygame_menu

from src.StateManager import StateManager
from src.Tile import Tile
from src.TileException import TileException


class Background(Enum):
    normal = 1
    logos = 2
    mixed = 3


class MemoryGame:
    def __init__(self):
        self.state_manager = StateManager()
        self.max_collection_count = 8
        self.normal_images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg",
                              "biene.jpg", "pferd.jpg", "auto.jpg", "nebel.jpg"]
        self.logo_images = ["rust.jpg", "python.jpg", "java.jpg", "cpp.jpg",
                            "kotlin.jpg", "javascript.jpg", "ocaml.jpg", "go.jpg"]
        self.images = self.normal_images * 2
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        self.menu = pygame_menu.Menu(400, 600, 'Welcome', theme=pygame_menu.themes.THEME_SOLARIZED)

        self.menu.add_text_input('Name :', default='Spieler1')
        self.menu.add_selector('Tile Theme :', [('Normal', Background.normal), ('Logos', Background.logos),
                                                ('Mixed', Background.mixed)], onchange=self.set_tile_images)

        self.menu.add_button('Play', self.start_game)
        self.menu.add_button('Quit', pygame_menu.events.EXIT)
        self.menu.mainloop(self.screen)
        pygame.quit()

    def calculate_match_ratio(self) -> float:
        mismatches = self.state_manager.mismatches
        matches = self.state_manager.matches
        ratio = matches + mismatches

        if ratio == 0:
            return 0.0
        return matches / ratio

    def mix_lists(self, normal_images, logo_images):
        """
        :param normal_images: all default images
        :param logo_images: images of programming languages
        :return: mixed list of both
        :rtype: list
        """
        merged_length = len(normal_images) + len(logo_images)
        merged_list = (normal_images + logo_images)
        random.shuffle(merged_list)
        merge_ratio = 2 if merged_length == self.max_collection_count else 0.5
        return merged_list[:int(merged_length * merge_ratio)]

    def set_tile_images(self, value, tile_type):
        """
        :param value: tuple of selected tile theme in main screen
        :param tile_type: enum of type Background
        :rtype: void
        """
        if tile_type == Background.normal:
            self.images = self.normal_images * 2
        elif tile_type == Background.logos:
            self.images = self.logo_images * 2
        elif tile_type == Background.mixed:
            images = self.mix_lists(self.normal_images, self.logo_images)
            assert len(images) == self.max_collection_count
            self.images = images * 2
        else:
            raise RuntimeError("background type not supported")

    def start_game(self):
        tiles_count = int(self.max_collection_count / 2)
        border_size = 5
        grid_size = tiles_count * 65 - border_size
        self.screen = pygame.display.set_mode((grid_size, grid_size))
        tiles = self.prepare_tiles(tiles_count)
        self.game_loop(tiles)

    def check_click(self, tiles):
        """
        :param tiles: list of created tiles displayed by screen
        :return: returns if any tile has been clicked
        :rtype: bool
        """
        res = False
        for tile in tiles:
            has_capacity = self.state_manager.has_capacity()
            clicked = tile.handle_event(has_capacity)

            if clicked:
                res = res or clicked
                try:
                    self.state_manager.add_clicked_tile(tile)
                except TileException:
                    print("Can't add a new tile")
        return res

    def draw_tiles(self, tiles):
        """
        :param tiles: list of created tiles displayed by screen
        :rtype: void
        """
        for tile in tiles:
            tile.draw(self.screen)

    def update_screen(self, clock):
        """
        :rtype: void
        :param clock: pygame clock (https://www.pygame.org/docs/ref/time.html#pygame.time.Clock)
        """
        pygame.display.flip()
        clock.tick(30)
        pygame.display.update()

    def game_loop(self, tiles):
        """
        :param tiles: list of created tiles displayed by screen
        :rtype: void
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
                self.screen = pygame.display.set_mode((600, 400))

            """
            Using key 'c' to hide the incorrect matches.
            This is required because a thread based solution is asynchronous and
            therefore would need to sync events and state of tiles, 
            therefore interactions would be ambiguous
            """
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                if self.state_manager.is_full():
                    matches = self.state_manager.check_tiles(True, event)
                    if not matches:
                        self.state_manager.hide_tiles()
                    self.state_manager.clear_tiles()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                clicked = self.check_click(tiles)

                if self.state_manager.is_full() and self.state_manager.check_tiles(clicked, event):
                    self.state_manager.clear_tiles()
                self.check_finished(tiles)

            self.draw_tiles(tiles)
            self.update_screen(clock)

    def get_random_image(self, images):
        """
        :param images: list of chosen images in main screen
        :return: tuple of random selected image in image list and associated tile id
        :rtype: (str, str)
        """
        rand_image = random.choice(images)
        images.remove(rand_image)
        tile_id = Path(rand_image).resolve().stem
        return rand_image, tile_id

    def add_tile(self, y, x, tiles, images):
        """
        :rtype: void
        :param y: y-coordinate of selected tile
        :param x: x-coordinate of selected tile
        :param tiles: list of all created tiles
        :param images: list of available images
        """
        try:
            rand_image, tile_id = self.get_random_image(images)
            img = pygame.image.load('images/' + rand_image)

            cover = pygame.image.load('images/hidden.jpg')
            tile = Tile(x * 65, y * 65, img, cover, tile_id)
            tiles.append(tile)
        except IndexError:
            print("Can't find image for tile")

    def check_finished(self, tiles):
        """
        :param tiles: list of all displayed tiles
        :rtype: void
        """
        finished = all(not tile.covered for tile in tiles)

        if finished:
            print("Du hast das Spiel gewonnen!")
            print("Deine Statistiken:")
            print("Deine Genauigkeit: " + str(self.calculate_match_ratio() * 100.0) + "%")

    def prepare_tiles(self, tiles_count):
        """
        :param tiles_count: specifies the count of tiles fitting in each row/column
        :return: a list of tiles created by count of tiles
        :rtype: list
        """
        images = self.images
        random.shuffle(images)
        assert tiles_count <= math.sqrt(len(images))

        tiles = []
        # using itertools to flatten (merging 2 lists) and therefore optimizing startup time
        for y, x in itertools.product(range(tiles_count), range(tiles_count)):
            self.add_tile(y, x, tiles, images)
        return tiles
