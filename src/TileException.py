class TileException(Exception):
    """Exception raised for invalid tiles."""

    def __init__(self, message="Tile error."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
