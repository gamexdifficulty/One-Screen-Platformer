from frostlight_engine import *

from data.classes.tilemap import Tilemap
from data.classes.camera import Camera

class Game(Engine):
    def __init__(self):
        super().__init__(catch_error=False,delete_old_logs=True)
        self.tilemap = Tilemap(self)
        self.tilemap.load_tilemap(os.path.join("data","tilemap.json"))

    def update(self):
        if self.game_state == "intro":
            pass

        if self.game_state == "menu":
            pass

        if self.game_state == "game":
            pass

    def draw(self):
        if self.game_state == "intro":
            pass

        if self.game_state == "menu":
            pass

        if self.game_state == "game":
            pass

        self.tilemap.draw()


if __name__ == "__main__":
    game = Game()
    game.run()
