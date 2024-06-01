import os
import json
import pygame
from data.classes.player import Player
from data.classes.camera import Camera

class Tilemap:
    def __init__(self,engine) -> None:
        self.engine = engine
        self.tile_size = 0
        self.width = 0
        self.height = 0
        self.tilemap = []
        self.tile_sprites = {}
        self.sprite = pygame.Surface((self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
        self.camera = Camera(self.engine)

        self.load_config()

    def load_config(self):
        with open(os.path.join("data","tilemapconfig.json"),"r") as f:
            data = json.load(f)
            if "tile_size" in data:
                self.tile_size = data["tile_size"]
            if "width" in data:
                if type(data["width"]) == int:
                    self.width = data["width"]
                elif data["width"] == "screen":
                    self.width = int(1920/self.tile_size)
            if "height" in data:
                if type(data["height"]) == int:
                    self.height = data["height"]
                elif data["height"] == "screen":
                    self.height = int(1080/self.tile_size)
            if "sprites" in data:
                for tile in data["sprites"]:
                    if type(data["sprites"][tile]) == str:
                        self.tile_sprites[tile] = pygame.transform.scale(pygame.image.load(data["sprites"][tile]),(self.tile_size,self.tile_size)).convert_alpha()

    def load_tilemap(self,file:str):
        tilemap = []
        with open(file,"r") as f:
            data = json.load(f)
            if "tilemap" in data:
                tilemap = data["tilemap"]
        self.sprite = pygame.Surface((self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
        self.sprite.set_colorkey((0,0,0))
        self.sprite = pygame.transform.scale(self.sprite,(self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
        for y,layer in enumerate(tilemap):
            tile_layer = []
            for x,tile in enumerate(layer):
                tile_layer.append(tile)
                if tile != None:
                    self.sprite.blit(self.tile_sprites[tile],(x*self.tile_size,y*self.tile_size))
            self.tilemap.append(layer)
        self.camera.center_rect(pygame.Rect(0,0,self.width*self.tile_size,self.height*self.tile_size))

    def save_tilemap(self,file:str):
        with open(file,"r") as f:
            data = json.load(f)
            data["tilemap"] = self.tilemap
        with open(file,"w+") as f:
            json.dump(data,f)

    def new_tilemap(self,width,height):
        self.tilemap = []
        self.sprite = pygame.Surface((self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
        self.sprite.set_colorkey((0,0,0))
        self.sprite = pygame.transform.scale(self.sprite,(self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
        for y in range(height):
            layer = []
            for x in range(width):
                layer.append(None)
            self.tilemap.append(layer)

    def set_tile(self,x,y,tile):
        if self.tilemap[y][x] != tile:
            self.sprite = pygame.Surface((self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
            self.sprite.set_colorkey((0,0,0))
            self.sprite = pygame.transform.scale(self.sprite,(self.width*self.tile_size,self.height*self.tile_size)).convert_alpha()
            self.tilemap[y][x] = tile
            for y,layer in enumerate(self.tilemap):
                for x,tile in enumerate(layer):
                    if tile != None:
                        self.sprite.blit(self.tile_sprites[tile],(x*self.tile_size,y*self.tile_size))

    def get_collision(self,player:Player):
        pass

    def update(self):
        pass

    def draw(self):
        self.engine.window.render(self.sprite,(0+self.camera.x,0+self.camera.y))
        