import random
import arcade
import config


class FlyingObstacle(arcade.SpriteSolidColor):
    def __init__(self, height_type: str):
        super().__init__(
            width=50,
            height=30,
            color=arcade.color.GRAY,
        )

        self.center_x = config.SCREEN_WIDTH + 50

        if height_type == "low":
            self.center_y = config.BIRD_HEIGHT_LOW
        else:
            self.center_y = config.BIRD_HEIGHT_HIGH

    def update(self, delta_time: float):
        self.center_x -= config.OBSTACLE_SPEED * delta_time

        if self.right < 0:
            self.remove_from_sprite_lists()
