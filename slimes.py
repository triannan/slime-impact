import arcade
import os
from arcade.sprite import *
from globalVariables import *

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]
class Slimes(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = LEFT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        main_path = "sprites/slimes/waterSlime"

        self.idle_texture_pair = load_texture_pair(f"{main_path}0.png")

        self.slide_textures = []
        texture = load_texture_pair(f"{main_path}0.png")
        self.slide_textures.append(texture)
        texture = load_texture_pair(f"{main_path}1.png")
        self.slide_textures.append(texture)
        texture = load_texture_pair(f"{main_path}2.png")
        self.slide_textures.append(texture)
        texture = load_texture_pair(f"{main_path}3.png")
        self.slide_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        if self.change_x < 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        #sliding
        self.cur_texture += 1
        if self.cur_texture > 10:
            self.cur_texture = 0
        self.texture = self.slide_textures[self.cur_texture // 4][self.character_face_direction]