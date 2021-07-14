import arcade
import os
from arcade.sprite import *
from globalVariables import *
from lumine import *
from slimes import *

# "© All rights reserved by miHoYo. Other properties belong to their respective owners."


class StartScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("titleScreen.png")

        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = SlimeImpact()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)

class GameOverScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("gameOver.png")

        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        self.texture.draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = SlimeImpact()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)

class SlimeImpact(arcade.View):

    def __init__(self):
        super().__init__()
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.background = None

        self.mora_list = None
        self.primos_list = None
        self.wall_list = None
        self.player_list = None
        self.chest_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.player_sprite = None
        self.slime_list = None
        self.slime_sprite = None
        self.game_over = False

        self.view_bottom = 0
        self.view_left = 0
        self.end_of_map = 0
        self.level = 1
        self.primogems = 0
        self.moras = 0
        
        arcade.set_background_color(arcade.csscolor.ALICE_BLUE)

    def setup(self, level):
        self.view_bottom = 0
        self.view_left = 0
        self.primogems = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.mora_list = arcade.SpriteList()
        self.primos_list = arcade.SpriteList()
        self.chest_list = arcade.SpriteList()
        self.slime_list = arcade.SpriteList()

        self.background = arcade.load_texture("bg.png")

        self.player_sprite = Lumine()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        self.slime_sprite = Slimes()

        map_name = f"maps/map_level_{level}.tmx"
        platforms_layer_name = 'platforms'
        mora_layer_name = 'mora'
        primos_layer_name = 'primos'
        my_map = arcade.tilemap.read_tmx(map_name)

        if map_name == "maps/map_level_1.tmx":
            self.slime_sprite.center_x = 1000
            self.slime_sprite.center_y = 380
            self.slime_sprite.change_x = 2
            self.slime_list.append(self.slime_sprite)

        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        self.wall_list = arcade.tilemap.process_layer(my_map, platforms_layer_name, TILE_SCALING, use_spatial_hash=True)
        self.mora_list = arcade.tilemap.process_layer(my_map, mora_layer_name, TILE_SCALING)
        self.primos_list = arcade.tilemap.process_layer(my_map, primos_layer_name, TILE_SCALING)
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

            
    def process_keychange(self):
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers): 

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_draw(self):
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(0, 0, 1600, 1280, self.background)

        self.wall_list.draw()
        self.mora_list.draw()
        self.primos_list.draw()
        self.player_list.draw()
        self.chest_list.draw()
        self.slime_list.draw()

        mora_text = f"mora: {self.moras}"
        arcade.draw_text(mora_text, 10 + self.view_left, 615 + self.view_bottom, arcade.csscolor.WHITE, 18)

        primo_text = f"primogems: {self.primogems}"
        arcade.draw_text(primo_text, 10 + self.view_left, 590 + self.view_bottom, arcade.csscolor.WHITE, 18)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.slime_list.update_animation()

        if not self.game_over:
            if self.physics_engine.can_jump():
                self.player_sprite.can_jump = False
            else:
                self.player_sprite.can_jump = True

            self.mora_list.update_animation(delta_time)
            self.player_list.update_animation(delta_time)

            self.slime_list.update()

            mora_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.mora_list)
            for mora in mora_hit_list:
                mora.remove_from_sprite_lists()
                self.moras += 1

            primos_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.primos_list)
            for primos in primos_hit_list:
                primos.remove_from_sprite_lists()
                self.primogems += 1
    
            changed_viewport = False

            left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
            if self.player_sprite.left < left_boundary:
                self.view_left -= left_boundary - self.player_sprite.left
                changed_viewport = True

            right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
            if self.player_sprite.right > right_boundary:
                self.view_left += self.player_sprite.right - right_boundary
                changed_viewport = True

            top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
            if self.player_sprite.top > top_boundary:
                self.view_bottom += self.player_sprite.top - top_boundary
                changed_viewport = True

            bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
            if self.player_sprite.bottom < bottom_boundary:
                self.view_bottom -= bottom_boundary - self.player_sprite.bottom
                changed_viewport = True

            if self.player_sprite.center_x >= self.end_of_map:
                self.level += 1
                self.setup(self.level)

                self.view_left = 0
                self.view_bottom = 0
                changed_viewport = True

            if changed_viewport:
                self.view_bottom = int(self.view_bottom)
                self.view_left = int(self.view_left)
                if self.player_sprite.left <= RIGHT_VIEWPORT_MARGIN: 
                    self.view_left = 0
                elif self.player_sprite.right >= self.end_of_map - 250:
                    self.view_left = self.end_of_map - SCREEN_WIDTH
                arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

            if self.player_sprite.center_y < -500:
                view = GameOverScreen()
                self.window.show_view(view)

            for slime in self.slime_list:
                if len(arcade.check_for_collision_with_list(slime, self.wall_list)) > 0:
                    slime.change_x *= -1
                elif slime.boundary_left is not None and slime.left < slime.boundary_left:
                    slime.change_x *= -1
                elif slime.boundary_right is not None and slime.right > slime.boundary_right:
                    slime.change_x *= -1

            if len(arcade.check_for_collision_with_list(self.player_sprite, self.slime_list)) > 0:
                self.game_over = True
                view = GameOverScreen()
                self.window.show_view(view)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartScreen()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()