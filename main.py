from frostlight_engine import *

from data.classes.tilemap import Tilemap
from data.classes.player import Player
from data.classes.camera import Camera

class Game(Engine):
    def __init__(self):
        super().__init__(catch_error=False,delete_old_logs=True)
        self.game_version = "0.0.1"
        self.camera = Camera(self)
        self.tilemap = Tilemap(self,camera=self.camera)
        self.player = Player(self,400,400,camera=self.camera)
        self.tilemap.load_tilemap(os.path.join("data","tilemap.json"))

    def update(self):
        self.window.set_name(self.window.get_fps())
        if self.game_state == "intro":
            pass

        if self.game_state == "menu":
            pass

        if self.game_state == "game":
            pass
        
        self.player.update()

    def draw(self):
        self.window.fill([100,100,100])
        if self.game_state == "intro":
            pass

        if self.game_state == "menu":
            pass

        if self.game_state == "game":
            pass

        self.tilemap.draw()
        self.player.draw()

if __name__ == "__main__":
    game = Game()
    game.run()
