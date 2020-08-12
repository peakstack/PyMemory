class StateManager:
    def __init__(self):
        self.current_flipped_tiles = []
        self.max_tiles = 2

    def add_clicked_tile(self, tile):
        if len(self.current_flipped_tiles) < self.max_tiles:
            self.current_flipped_tiles.append(tile)
            print(tile.tile_id + " tile added")
        else:
            raise RuntimeError("Can't add new tile")

    def has_capacity(self):
        return len(self.current_flipped_tiles) < self.max_tiles

    def hide_tiles(self):
        for tile in self.current_flipped_tiles:
            tile.set_covered(True)

    def clear_tiles(self):
        self.current_flipped_tiles.clear()

    def is_full(self):
        return len(self.current_flipped_tiles) == self.max_tiles

    def check_tiles(self):
        first_tile = self.current_flipped_tiles[0]
        second_tile = self.current_flipped_tiles[1]
        return first_tile.tile_id == second_tile.tile_id
