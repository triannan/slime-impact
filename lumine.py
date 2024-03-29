import arcade
import os
from arcade.sprite import *
from globalVariables import *

def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class Lumine(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        self.jumping = False

        main_path = "sprites/lumine1/lumine"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_front.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_front.png")

        self.walk_textures = []
        texture = load_texture_pair(f"{main_path}_walk0.png")
        self.walk_textures.append(texture)
        texture = load_texture_pair(f"{main_path}_walk1.png")
        self.walk_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        #walking
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // 4][self.character_face_direction]