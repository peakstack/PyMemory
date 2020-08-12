import pygame


class Tile:
    def __init__(self, x, y, image, cover, tile_id):
        self.image = image
        self.cover = cover
        self.rect = pygame.Rect(x, y, 60, 60)
        self.covered = True
        self.time_to_cover = None
        self.tile_id = tile_id

    def check_clicked(self, has_capacity):
        x, y = pygame.mouse.get_pos()

        if not has_capacity:
            return False

        if not (self.rect.collidepoint(x, y) and self.covered):
            return False

        self.covered = not self.covered
        return True

    def handle_event(self, has_capacity):
        return self.check_clicked(has_capacity)

    def set_covered(self, val):
        self.covered = val

    def draw(self, screen):
        if self.covered:
            screen.blit(self.cover, self.rect)
        else:
            screen.blit(self.image, self.rect)
