from frostlight_engine import *

class Game(Engine):
    def __init__(self):
        super().__init__() # Engine options go here

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


if __name__ == "__main__":
    game = Game()
    game.run()
