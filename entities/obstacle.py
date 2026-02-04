import arcade
import config


class Obstacle(arcade.SpriteSolidColor):
    def __init__(self):
        super().__init__(
            config.OBSTACLE_WIDTH,
            config.OBSTACLE_HEIGHT,
            arcade.color.RED,
        )

        self.center_x = config.SCREEN_WIDTH + config.OBSTACLE_WIDTH
        self.center_y = config.GROUND_Y + config.OBSTACLE_HEIGHT // 2

    def update(self, delta_time: float = 0) -> None:
        self.center_x -= config.OBSTACLE_SPEED * delta_time

        if self.right < 0:
            self.remove_from_sprite_lists()
