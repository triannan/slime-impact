import arcade
import os
# "© All rights reserved by miHoYo. Other properties belong to their respective owners."
SCREEN_WIDTH = 1000
SCREEN_HEIGHT =650
SCREEN_TITLE = "slime impact!"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = .6
PLAYER_JUMP_SPEED = 15

LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = SPRITE_PIXEL_SIZE * TILE_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 1

RIGHT_FACING = 0
LEFT_FACING = 1

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
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---

        main_path = "sprites/lumine1/lumine"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_front.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_front.png")

        # Load textures for walking
        self.walk_textures = []
        texture = load_texture_pair(f"{main_path}_walk0.png")
        self.walk_textures.append(texture)
        texture = load_texture_pair(f"{main_path}_walk1.png")
        self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Jumping animation
        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // 4][self.character_face_direction]

class Slimes(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # --- Load Textures ---

        main_path = "sprites/slimes/waterSlime"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}1.png")

        # Load textures for walking
        self.walk_textures = []
        texture = load_texture_pair(f"{main_path}1.png")
        self.walk_textures.append(texture)
        texture = load_texture_pair(f"{main_path}2.png")
        self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // 4][self.character_face_direction]

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

        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.chest_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.player_sprite = None
        self.game_over = False

        self.view_bottom = 0
        self.view_left = 0

        self.end_of_map = 0
        self.level = 1

    def setup(self, level):
        self.view_bottom = 0
        self.view_left = 0

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.chest_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        img = "sprites/lumine1/lumine_front.png"
        self.player_sprite = Lumine()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # Name of map file to load
        map_name = f"map_level_{level}.tmx"

        if map_name == "map_level_1.tmx":
            enemy = Slimes()
            enemy.bottom = SPRITE_PIXEL_SIZE * 2.5
            enemy.left = SPRITE_PIXEL_SIZE * 6.5
            enemy.change_x = 2
            self.enemy_list.append(enemy)

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'coins'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

        #self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_draw(self):
        arcade.start_render()

        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()
        self.chest_list.draw()
        self.enemy_list.draw()

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True

        # Process left/right
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
    
    def on_update(self, delta_time):
        self.physics_engine.update()

        if not self.game_over:
            if self.physics_engine.can_jump():
                self.player_sprite.can_jump = False
            else:
                self.player_sprite.can_jump = True

            self.coin_list.update_animation(delta_time)
            self.player_list.update_animation(delta_time)

            self.enemy_list.update()
            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
    
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
                elif self.player_sprite.left >= self.end_of_map:
                    self.view_left = self.end_of_map - RIGHT_VIEWPORT_MARGIN
                arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

            if self.player_sprite.center_y < -100:
                view = GameOverScreen()
                self.window.show_view(view)


            for enemy in self.enemy_list:
                # If the enemy hit a wall, reverse
                if len(arcade.check_for_collision_with_list(enemy, self.wall_list)) > 0:
                    enemy.change_x *= -1
                # If the enemy hit the left boundary, reverse
                elif enemy.boundary_left is not None and enemy.left < enemy.boundary_left:
                    enemy.change_x *= -1
                # If the enemy hit the right boundary, reverse
                elif enemy.boundary_right is not None and enemy.right > enemy.boundary_right:
                    enemy.change_x *= -1

            if len(arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)) > 0:
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