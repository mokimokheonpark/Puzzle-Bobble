import math
import pygame

import constants

class Bubble(pygame.sprite.Sprite):
    
    def __init__(self, image, color, position = (0, 0), row_idx = -1, col_idx = -1):
        super().__init__()
        self.image = image
        self.color = color
        self.rect = image.get_rect(center = position)
        self.radius = 18
        self.row_idx = row_idx
        self.col_idx = col_idx
    
    def set_rect(self, position):
        self.rect = self.image.get_rect(center = position)

    def draw(self, screen, to_x = None):
        if to_x:
            screen.blit(self.image, (self.rect.x + to_x, self.rect.y))
        else:
            screen.blit(self.image, self.rect)
    
    def set_angle(self, angle):
        self.angle = angle
        self.rad_angle = math.radians(self.angle)
    
    def move(self):
        to_x = self.radius * math.cos(self.rad_angle)
        to_y = self.radius * math.sin(self.rad_angle) * -1

        self.rect.x += to_x
        self.rect.y += to_y

        if self.rect.left < 0 or self.rect.right > constants.SCREEN_WIDTH:
            self.set_angle(180 - self.angle)
    
    def set_map_index(self, row_idx, col_idx):
        self.row_idx = row_idx
        self.col_idx = col_idx
    
    def drop_downward(self, height):
        self.rect = self.image.get_rect(center = (self.rect.centerx, self.rect.centery + height))