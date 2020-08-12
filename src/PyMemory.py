import pygame
import itertools
import random
from pathlib import Path

from src.StateManager import StateManager
from src.Tile import Tile


def check_action(tiles, state_manager):
    for tile in tiles:
        has_capacity = state_manager.has_capacity()
        clicked = tile.handle_event(has_capacity)

        if clicked:
            state_manager.add_clicked_tile(tile)


def draw_tiles(tiles, screen):
    for tile in tiles:
        tile.draw(screen)


def reset_screen(clock):
    pygame.display.flip()
    clock.tick(30)
    pygame.display.update()


def game_loop(tiles, screen, state_manager):
    clock = pygame.time.Clock()
    last = pygame.time.get_ticks()
    cool_down = 1000
    running = True

    while running:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            check_action(tiles, state_manager)

        is_full = state_manager.is_full()

        if is_full:
            now = pygame.time.get_ticks()

            diff = now - last
            if diff >= cool_down:
                last = now
                matches = state_manager.check_tiles()
                if not matches:
                    state_manager.hide_tiles()
                state_manager.clear_tiles()

        draw_tiles(tiles, screen)
        reset_screen(clock)


def get_random_image(images):
    rand_image = random.choice(images)
    images.remove(rand_image)
    tile_id = Path(rand_image).resolve().stem
    return rand_image, tile_id


def add_tile(y, x, tiles, images):
    rand_image, tile_id = get_random_image(images)
    img = pygame.image.load('images/' + rand_image)

    cover = pygame.image.load('images/hidden.jpg')
    tile = Tile(x * 65, y * 65, img, cover, tile_id)
    tiles.append(tile)


def prepare_tiles():
    images = ["blume.jpg", "bus.jpg", "bagger.jpg", "erde.jpg", "biene.jpg", "pferd.jpg", "auto.jpg", "nebel.jpg"] * 2
    random.shuffle(images)

    tiles = []
    for y, x in itertools.product(range(4), range(4)):
        add_tile(y, x, tiles, images)
    return tiles


def main():
    state_manager = StateManager()
    pygame.init()
    tiles_count = 4
    border_size = 5
    grid_size = tiles_count * 65 - border_size
    screen = pygame.display.set_mode((grid_size, grid_size))

    tiles = prepare_tiles()

    game_loop(tiles, screen, state_manager)
    pygame.quit()


if __name__ == '__main__':
    main()
