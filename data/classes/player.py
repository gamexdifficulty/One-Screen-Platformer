import os
import json
import numpy
import pygame
from data.classes.camera import Camera

class Player:
    def __init__(self,engine,x=0.0,y=0.0,camera:Camera=None) -> None:
        self.engine = engine
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.coyote_time = 0.0
        self.jump_buffer = 0.0
        self.stop = 1
        self.on_floor = False

        self.sprites = []

        self.camera = camera
        if camera == None:
            self.camera = Camera(self.engine)

        self.JUMP_BUTTON = "accept"
        self.LEFT_BUTTON = "left"
        self.RIGHT_BUTTON = "right"

        self.SIZE = 0
        self.multiplier = 1

        self.ACC = 0
        self.DCC = 0
        self.GRAVITY = 0
        self.MAX_X_VEL = 0
        self.MAX_GRAVITY = 0
        self.MAX_COYOTE_TIME = 0
        self.MAX_JUMP_BUFFER = 0
        self.JUMP_STRENGTH = 0

        self.load_config()

    def load_config(self):
        with open(os.path.join("data","playerconfig.json"),"r") as f:
            data = json.load(f)
            if "acc" in data:
                self.ACC = data["acc"]
            if "dcc" in data:
                self.DCC = data["dcc"]
            if "vel" in data:
                self.MAX_X_VEL = data["vel"]
            if "jump" in data:
                self.JUMP_STRENGTH = data["jump"]
            if "gravity" in data:
                self.GRAVITY = data["gravity"]
            if "max_gravity" in data:
                self.MAX_GRAVITY = data["max_gravity"]
            if "coyote_time" in data:
                self.MAX_COYOTE_TIME = data["coyote_time"]
            if "jump_buffer" in data:
                self.MAX_JUMP_BUFFER = data["jump_buffer"]
            if "size" in data:
                self.SIZE = data["size"]
            if "sprites" in data:
                if type(data["sprites"]) == list:
                    for path in data["sprites"]:
                        self.sprites.append(pygame.transform.scale(pygame.image.load(path),(self.SIZE,self.SIZE)))

    def update(self):
        collision_rects = self.engine.tilemap.get_collisions(self,1)
        
        if self.coyote_time > 0:
            self.coyote_time = max(self.coyote_time-self.engine.delta_time,0)

        if self.jump_buffer > 0:
            self.jump_buffer = max(self.jump_buffer-self.engine.delta_time,0)

        # Gravity

        self.vel_y += self.GRAVITY*self.engine.delta_time
        self.vel_y = min(self.vel_y,self.MAX_GRAVITY)

        # Jumping

        if self.engine.input.get(self.JUMP_BUTTON):
            if self.coyote_time > 0 or self.on_floor:
                self.vel_y = -self.JUMP_STRENGTH
                self.on_floor = False
                self.coyote_time = 0
            else:
                self.jump_buffer = self.MAX_JUMP_BUFFER

        # Movement

        self.multiplier = 1 + 0.5 * (numpy.sign(self.vel_x) != self.engine.input.get(self.RIGHT_BUTTON)-self.engine.input.get(self.LEFT_BUTTON))
        self.vel_x = self.vel_x * int(not (self.vel_x < self.stop and self.vel_x > -self.stop and not self.engine.input.get(self.RIGHT_BUTTON) and not self.engine.input.get(self.LEFT_BUTTON)))
        self.vel_x += (self.engine.input.get(self.RIGHT_BUTTON)-self.engine.input.get(self.LEFT_BUTTON))*self.ACC*self.multiplier*self.engine.delta_time
        self.vel_x += numpy.sign(self.vel_x) * -1 * self.DCC * self.engine.delta_time * int(not(numpy.sign(self.engine.input.get(self.RIGHT_BUTTON)-self.engine.input.get(self.LEFT_BUTTON))))
        self.vel_x = max(min(self.vel_x,self.MAX_X_VEL),-self.MAX_X_VEL)
        self.x += self.vel_x * self.engine.delta_time

        # Collisions

        self.x += self.vel_x*self.engine.delta_time
        for rect in collision_rects:
            player_rect = pygame.FRect(self.x,self.y,self.SIZE,self.SIZE)
            if player_rect.colliderect(rect):
                if self.vel_x > 0:
                    self.x = rect.left - self.engine.tilemap.tile_size
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.x = rect.right
                    self.vel_x = 0

        self.y += self.vel_y*self.engine.delta_time
        for rect in collision_rects:
            player_rect = pygame.FRect(self.x,self.y,self.SIZE,self.SIZE)
            if player_rect.colliderect(rect):
                if self.vel_y > 0:
                    self.y = rect.top - self.engine.tilemap.tile_size
                    self.vel_y = 0
                    self.on_floor = True
                    self.coyote_time = 0
                    if self.jump_buffer > 0:
                        self.vel_y = -self.JUMP_STRENGTH
                    self.jump_buffer = 0.0
                elif self.vel_y < 0:
                    self.y = rect.bottom
                    self.vel_y = 0

        if self.on_floor and self.vel_y != 0:
            self.on_floor = False
            self.coyote_time = self.MAX_COYOTE_TIME
    
    def draw(self):
        self.engine.window.render(self.sprites[0],(self.x+self.camera.x,self.y+self.camera.y))