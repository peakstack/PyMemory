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
        pygame.init()
        self.max_collection_count = 8
        self.normal_images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg",
                              "biene.jpg", "pferd.jpg", "auto.jpg", "nebel.jpg"]
        self.logo_images = ["rust.jpg", "python.jpg", "java.jpg", "cpp.jpg",
                            "kotlin.jpg", "javascript.jpg", "ocaml.jpg", "go.jpg"]
        self.images = None
        self.screen = pygame.display.set_mode((600, 400))
        self.menu = pygame_menu.Menu(400, 600, 'Welcome', theme=pygame_menu.themes.THEME_GREEN)

        self.menu.add_text_input('Name :', default='Spieler1')
        self.menu.add_selector('Tile Theme :', [('Normal', Background.normal), ('Logos', Background.logos),
                                                ('Mixed', Background.mixed)], onchange=self.set_tile_images)
        self.menu.add_button('Play', self.start_game)
        self.menu.add_button('Quit', pygame_menu.events.EXIT)
        self.menu.mainloop(self.screen)
        pygame.quit()

    def set_tile_images(self, value, tile_type):
        if tile_type == Background.normal:
            self.images = self.normal_images * 2

        elif tile_type == Background.logos:
            self.images = self.logo_images * 2
        elif tile_type == Background.mixed:
            merged_length = len(self.normal_images) + len(self.logo_images)

            if merged_length == self.max_collection_count * 2:
                images = (self.normal_images + self.logo_images)[:self.max_collection_count]
            else:
                images = (self.normal_images + self.logo_images)[:merged_length / 2]

            assert len(images) == self.max_collection_count

            self.images = self.logo_images * 2
        else:
            raise RuntimeError("background type not supported")

    def start_game(self):
        tiles_count = 4
        border_size = 5
        grid_size = tiles_count * 65 - border_size
        self.screen = pygame.display.set_mode((grid_size, grid_size))
        tiles = self.prepare_tiles(tiles_count)
        self.game_loop(tiles)

    def check_click(self, tiles):
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
        for tile in tiles:
            tile.draw(self.screen)

    def reset_screen(self, clock):
        pygame.display.flip()
        clock.tick(30)
        pygame.display.update()

    def game_loop(self, tiles):
        clock = pygame.time.Clock()
        running = True

        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
                self.screen = pygame.display.set_mode((600, 400))

            """
            Das Programm verwendet den Key 'c' um die nicht passenden Karten umzudrehen, da
            die clock des Programmes nicht warten kann. 
            Eine thread-basierte Lösung ist ebenfalls nicht realisierbar, da es sonst zu Komplikationen mit
            dem Interagieren der Tiles kommt
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
            self.reset_screen(clock)

    def get_random_image(self, images):
        rand_image = random.choice(images)
        images.remove(rand_image)
        tile_id = Path(rand_image).resolve().stem
        return rand_image, tile_id

    def add_tile(self, y, x, tiles, images):
        try:
            rand_image, tile_id = self.get_random_image(images)
            img = pygame.image.load('images/' + rand_image)

            cover = pygame.image.load('images/hidden.jpg')
            tile = Tile(x * 65, y * 65, img, cover, tile_id)
            tiles.append(tile)
        except IndexError:
            print("Can't find image for tile")

    def check_finished(self, tiles):
        finished = True
        for tile in tiles:
            finished = finished and not tile.covered

        if finished:
            print("Du hast das Spiel gewonnen!")
            print("Deine Statistiken:")
            print("Deine Genauigkeit: " + str((self.state_manager.matches / self.state_manager.matches) * 100))

    def prepare_tiles(self, tiles_count):
        images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg", "biene.jpg", "pferd.jpg", "auto.jpg",
                  "nebel.jpg"] * 2
        random.shuffle(images)

        assert tiles_count <= math.sqrt(len(images))

        tiles = []
        # itertools benutzt um die loop zu "flatten" und die startup-zeit zu vermindern
        for y, x in itertools.product(range(tiles_count), range(tiles_count)):
            self.add_tile(y, x, tiles, images)
        return tiles
