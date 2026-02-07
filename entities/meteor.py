import arcade
import config


class Meteor(arcade.SpriteSolidColor):
    def __init__(self, x: float, y: float):
        super().__init__(18, 18, center_x=x, center_y=y, color=arcade.color.BLACK)
        self.velocity_x = config.OBSTACLE_SPEED * 1.3

    def update(self, delta_time: float):
        self.center_x -= self.velocity_x * config.GAME_SPEED_MULTIPLIER * delta_time
        if self.right < 0:
            self.remove_from_sprite_lists()
