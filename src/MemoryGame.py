import itertools
import math
import random
from enum import Enum
from pathlib import Path
from os import listdir
from os.path import isfile, join

import pygame
import pygame_menu

from src.PlayerStatistics import PlayerStatistics
from src.StateManager import StateManager
from src.Tile import Tile
from src.TileException import TileException


class Background(Enum):
    NORMAL = 1
    LOGOS = 2
    MIXED = 3
    CUSTOM = 4


class MemoryGame:
    def __init__(self):
        self.username = "Spieler1"
        self.player_statistics = PlayerStatistics()
        self.player_statistics.load_from_file()
        self.game_mode = Background.NORMAL
        self.custom_images_path = "../images/custom"
        self.state_manager = StateManager()
        self.normal_images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg",
                              "biene.jpg", "pferd.jpg", "auto.jpg", "nebel.jpg"]
        self.logo_images = ["rust.jpg", "python.jpg", "java.jpg", "cpp.jpg",
                            "kotlin.jpg", "javascript.jpg", "ocaml.jpg", "go.jpg"]
        self.images = self.normal_images * 2
        self.max_collection_count = 8
        pygame.init()
        pygame.display.set_icon(pygame.image.load('../images/hidden.jpg'))
        pygame.display.set_caption('PyMemory - Teste dein Gedächtnis')
        self.screen = pygame.display.set_mode((600, 400))
        self.menu = pygame_menu.Menu(400, 600, 'Willkommen', theme=pygame_menu.themes.THEME_SOLARIZED)
        self.menu.add_text_input('Name: ', default=self.username, onchange=self.set_username)
        self.menu.add_selector('Hintergrund: ', [('Normal', Background.NORMAL), ('Logos', Background.LOGOS),
                                                 ('Gemischt', Background.MIXED),
                                                 ('Benutzerdefiniert', Background.CUSTOM)],
                               onchange=self.set_tile_images)
        self.menu.add_selector('Spielgröße: ', [('4x4', 4)],
                               onchange=self.change_tile_count)
        self.label = self.menu.add_label(title='Highscore: Nicht vorhanden', label_id='highscore', selectable=True)
        self.menu.add_button('Spielen', self.start_game)
        self.menu.add_button('Beenden', pygame_menu.events.EXIT)
        self.refresh_stats(self.username)
        self.menu.mainloop(self.screen)
        pygame.quit()

    def set_username(self, username):
        self.username = username
        self.refresh_stats(username)

    def refresh_stats(self, username):
        high_score = self.player_statistics.get_highscore(username)
        high_score_display = 'Highscore: ' + str(high_score) + "%" if high_score is not None else 'Highscore: Nicht ' \
                                                                                                  'vorhanden '
        self.label.set_title(high_score_display)

    def reset(self):
        self.normal_images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg",
                              "biene.jpg", "pferd.jpg", "auto.jpg", "nebel.jpg"]
        self.logo_images = ["rust.jpg", "python.jpg", "java.jpg", "cpp.jpg",
                            "kotlin.jpg", "javascript.jpg", "ocaml.jpg", "go.jpg"]
        self.images = self.normal_images * 2
        self.set_tile_images(None, self.game_mode)
        self.state_manager.clear_tiles()
        self.refresh_stats(self.username)

    def change_tile_count(self, value, tile_count):
        self.max_collection_count = tile_count * 2

    def calculate_match_ratio(self) -> float:
        mismatches = self.state_manager.mismatches
        matches = self.state_manager.matches
        ratio = matches + mismatches

        if ratio == 0:
            return 0.0
        return round(matches / ratio, 2)

    def mix_lists_fit(self, normal_images, logo_images):
        """
        :param normal_images: all default images fit
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
        if tile_type == Background.NORMAL:
            self.images = self.normal_images * 2
        elif tile_type == Background.LOGOS:
            self.images = self.logo_images * 2
        elif tile_type == Background.MIXED:
            images = self.mix_lists_fit(self.normal_images, self.logo_images)
            self.images = images * 2
        elif tile_type == Background.CUSTOM:
            file_names = [('custom/' + f) for f in listdir(self.custom_images_path)
                          if isfile(join(self.custom_images_path, f))]
            random.shuffle(file_names)
            self.images = file_names[:self.max_collection_count] * 2
        else:
            raise RuntimeError("background type not supported")
        self.game_mode = tile_type

    def start_game(self):
        tiles_count = int(self.max_collection_count / 2)
        border_size = 5
        space_size = 65
        grid_size = tiles_count * space_size - border_size
        self.screen = pygame.display.set_mode((grid_size, grid_size))
        tiles = self.prepare_tiles(tiles_count, space_size)
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.screen = pygame.display.set_mode((600, 400))
                    self.reset()
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

    def add_tile(self, y, x, tiles, images, space_size):
        """
        :param space_size: size of the space between the tiles
        :rtype: void
        :param y: y-coordinate of selected tile
        :param x: x-coordinate of selected tile
        :param tiles: list of all created tiles
        :param images: list of available images
        """
        try:
            rand_image, tile_id = self.get_random_image(images)
            img = pygame.image.load('../images/' + rand_image)

            cover = pygame.image.load('../images/hidden.jpg')
            tile = Tile(x * space_size, y * space_size, img, cover, tile_id)
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
            ratio = round(self.calculate_match_ratio() * 100.0, 2)

            print("Du hast das Spiel gewonnen!")
            print("Deine Statistiken:")
            print("Deine Genauigkeit: " + str(ratio) + "%")

            if self.player_statistics.is_new_highscore(self.username, ratio):
                print("Du hast einen neuen Highscore!")

            self.player_statistics.update_player(self.username, ratio)
            self.reset()

    def prepare_tiles(self, tiles_count, space_size):
        """
        :param space_size: size of the space between the tiles
        :param tiles_count: specifies the count of tiles fitting in each row/column
        :return: a list of tiles created by count of tiles
        :rtype: list
        """
        images = self.images

        if len(images) == 0:
            self.images = self.mix_lists_fit(self.normal_images, self.logo_images)

        random.shuffle(images)
        # asserting the quadratic property of the game field
        """
                        
                        tiles_count, e.g. 4     therefore we assume that the product of it is quadratic
                            # # # #             available tiles = 16, asserted tiles = 4
        tiles_count, e.g. 4 # # # #             4 <= sqrt(16) // -> True
                            # # # #             asserted tiles = 5 ->   5 <= sqrt(16)   // -> False
                            # # # #             if we have a tile_count of 5x5 then it would not fit
                                                25 would fit into 5x5, but 25 is odd so therefore is 1 card left
                                                36 would fit into 6x6, but I only have 16 cards available and this would 
                                                make up 16*2 = 32 cards
        """
        assert tiles_count <= math.sqrt(len(images))
        tiles = []
        # using itertools to flatten (merging 2 lists) and therefore optimizing startup time
        for y, x in itertools.product(range(tiles_count), range(tiles_count)):
            self.add_tile(y, x, tiles, images, space_size)
        return tiles


if __name__ == '__main__':
    game = MemoryGame()
