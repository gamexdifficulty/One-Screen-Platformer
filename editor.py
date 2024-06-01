from frostlight_engine import *

from data.classes.tilemap import Tilemap
from data.classes.camera import Camera

class Game(Engine):
    def __init__(self):
        super().__init__(catch_error=False,delete_old_logs=True) # Engine options go here
        self.tilemap = Tilemap(self)
        self.tilemap.load_tilemap(os.path.join("data","tilemap.json"))
        self.input.new("place",MOUSE_LEFTCLICK,PRESSED)
        self.input.new("delete",MOUSE_RIGHTCLICK,PRESSED)
        self.input.new("up",KEY_ARROW_UP,PRESSED)
        self.input.new("down",KEY_ARROW_UP,PRESSED)
        self.input.new("grid",KEY_G,CLICKED)
        self.input.new("quit",KEY_ESCAPE,PRESSED)
        self.grid = True
        self.tile_selected = "0"
        self.tile_bar_sprite = pygame.Surface((1920,200)).convert_alpha()
        self.tile_bar_rect = pygame.Rect(0,880,1920,200)
        pygame.draw.rect(self.tile_bar_sprite,(20,26,42),pygame.Rect(0,0,1920,200))
        self.tile_bar_sprite.set_alpha(150)

    def event_quit(self):
        self.tilemap.save_tilemap(os.path.join("data","tilemap.json"))

    def update(self):
        self.window.set_name(self.window.get_fps())
        if self.input.get("place"):
            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    rect = pygame.Rect(x*self.tilemap.tile_size+self.tilemap.camera.x,y*self.tilemap.tile_size+self.tilemap.camera.y,self.tilemap.tile_size,self.tilemap.tile_size)
                    if rect.collidepoint(self.input.mouse.get_pos()) and not self.tile_bar_rect.collidepoint(self.input.mouse.get_pos()):
                        self.tilemap.set_tile(x,y,self.tile_selected)

            for i,tile in enumerate(self.tilemap.tile_sprites):
                rect = pygame.Rect(32+(self.tilemap.tile_size+8)*i,896,self.tilemap.tile_size,self.tilemap.tile_size)
                if rect.collidepoint(self.input.mouse.get_pos()):
                    self.tile_selected = tile

        elif self.input.get("delete"):
            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    rect = pygame.Rect(x*self.tilemap.tile_size+self.tilemap.camera.x,y*self.tilemap.tile_size+self.tilemap.camera.y,self.tilemap.tile_size,self.tilemap.tile_size)
                    if rect.collidepoint(self.input.mouse.get_pos()) and not self.tile_bar_rect.collidepoint(self.input.mouse.get_pos()):
                        self.tilemap.set_tile(x,y,None)

        if self.input.get("grid"):
            self.grid = not self.grid
        if self.input.get("up"):
            self.tilemap.camera.set_pos(0,self.tilemap.camera.y-300*self.delta_time)
        elif self.input.get("down"):
            self.tilemap.camera.set_pos(0,self.tilemap.camera.y+300*self.delta_time)
        if self.input.get("quit"):
            self.quit()

    def draw(self):
        self.window.fill((3,13,37))
        self.tilemap.draw()
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                rect = pygame.Rect(x*self.tilemap.tile_size+self.tilemap.camera.x,y*self.tilemap.tile_size+self.tilemap.camera.y,self.tilemap.tile_size,self.tilemap.tile_size)
                if self.grid:
                    pygame.draw.rect(self.window.main_surface,(7,132,227),rect,1)

        self.window.render(self.tile_bar_sprite,(0,880))
        for i,tile in enumerate(self.tilemap.tile_sprites):
            rect = pygame.Rect(32+(self.tilemap.tile_size+8)*i,896,self.tilemap.tile_size,self.tilemap.tile_size)
            self.window.render(self.tilemap.tile_sprites[tile],(rect.x,rect.y))
            if self.tile_selected == tile:
                pygame.draw.rect(self.window.main_surface,(7,132,227),rect,1)

if __name__ == "__main__":
    game = Game()
    game.run()
