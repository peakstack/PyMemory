import pygame

from TileException import TileException


class StateManager:
    def __init__(self):
        self.current_flipped_tiles = []
        self.max_tiles = 2
        self.matches = 0
        self.mismatches = 0

    def add_clicked_tile(self, tile):
        if self.has_capacity():
            self.current_flipped_tiles.append(tile)
        else:
            raise TileException("Can't add new tile")

    def has_capacity(self):
        return len(self.current_flipped_tiles) < self.max_tiles

    def hide_tiles(self):
        for tile in self.current_flipped_tiles:
            tile.set_covered(True)

    def clear_tiles(self):
        self.current_flipped_tiles.clear()

    def is_full(self):
        return len(self.current_flipped_tiles) == self.max_tiles

    def check_tiles(self, clicked, event):
        if clicked:
            first_tile = self.current_flipped_tiles[0]
            second_tile = self.current_flipped_tiles[1]
            matching = first_tile.tile_id == second_tile.tile_id

            if event.type == pygame.MOUSEBUTTONDOWN:
                if matching:
                    self.matches += 1
                else:
                    self.mismatches += 1
            return matching
        return False
