import arcade
import config
from graphics.assets import load_texture_or_none


class Obstacle(arcade.SpriteSolidColor):
    def __init__(self):
        super().__init__(
            config.OBSTACLE_WIDTH,
            config.OBSTACLE_HEIGHT,
            arcade.color.BLACK,
        )
        tex = load_texture_or_none("assets/obstacles/cactus.png")
        if tex:
            self.texture = tex

        self.center_x = config.SCREEN_WIDTH + config.OBSTACLE_WIDTH
        self.center_y = config.GROUND_Y + config.OBSTACLE_HEIGHT // 2

    def update(self, delta_time: float = 0) -> None:
        self.center_x -= config.OBSTACLE_SPEED * config.GAME_SPEED_MULTIPLIER * delta_time

        if self.right < 0:
            self.remove_from_sprite_lists()
