import pygame 

class Camera:
    def __init__(self,engine,x=0,y=0,width=1920,height=1080) -> None:
        self.engine = engine
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_pos(self,x,y):
        self.x = x
        self.y = y

    def set_size(self,width,height):
        self.width = width
        self.height = height

    def center_rect(self,rect:pygame.Rect):
        self.x = self.width/2-rect.width/2
        self.y = self.height/2-rect.height/2