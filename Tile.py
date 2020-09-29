import pygame


class Tile:
    def __init__(self, x, y, image, cover, tile_id):
        self.image = image
        self.cover = cover
        self.rect = pygame.Rect(x, y, 60, 60)
        self.covered = True
        self.tile_id = tile_id

    def check_clicked(self, has_capacity) -> bool:
        # check for state that there are not more than 2 being displayed on the screen
        if not has_capacity:
            return False

        x, y = pygame.mouse.get_pos()

        # if mouse clicked this Tile and it has not been already clicked -> flip it
        if self.rect.collidepoint(x, y) and self.covered:
            self.flip()
            return True

    def handle_event(self, has_capacity) -> bool:
        return self.check_clicked(has_capacity)

    def set_covered(self, val):
        self.covered = val

    def flip(self):
        self.covered = not self.covered

    def draw(self, screen):
        # if screen is covered, display the cover, else the image
        if self.covered:
            screen.blit(self.cover, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def __str__(self):
        return f'{self.tile_id} -> {self.covered}'
