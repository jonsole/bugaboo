"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 200
GRAVITY = 300
PLAYER_JUMP_SPEED = 300

class Player(arcade.Sprite):
    """ Player Class """

    def __init__(self, platforms):
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        super().__init__(image_source, CHARACTER_SCALING)

        # Store platforms so we can do collision detection against them
        self.platforms = platforms

        # Assume we're not a platform at the start
        self.is_on_platform = False


    def jump(self):
        # We can only jump if we're standing on a platform
        if self.is_on_platform:
            self.change_y = PLAYER_JUMP_SPEED


    def on_update(self, delta_time):

        # move in left/right direction
        self.center_x += self.change_x * delta_time

        # get list of platforms we're touching before moving up/down
        touch_before = arcade.check_for_collision_with_list(self, self.platforms)

        # move in up/down direction, include gravity
        self.center_y += self.change_y * delta_time
        self.change_y = self.change_y - GRAVITY * delta_time

        # get list of platforms we're touching after moving up/down
        touch_after = arcade.check_for_collision_with_list(self, self.platforms)

        # if going up we not on a platform
        if self.change_y > 0:
            self.is_on_platform = False
        else:
            # if touching after but not before, we on a platform
            for t in touch_after:
                if t not in touch_before:

                    while arcade.check_for_collision(self, t):
                        self.center_y += 0.1

                    # we're on a platform
                    self.is_on_platform = True

                    # don't fall
                    self.change_y = 0



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = "bugaboo.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player(self.scene["Platforms"])
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.player_sprite
        self.scene.add_sprite("Player", self.player_sprite)

        # --- Other stuff

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)


    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.jump()

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Update player position
        self.player_sprite.on_update(delta_time)

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()