import arcade
import config
from graphics.assets import load_texture_or_none


class Coin(arcade.SpriteSolidColor):
    def __init__(self, x: float, y: float):
        super().__init__(20, 20, center_x=x, center_y=y, color=arcade.color.YELLOW)
        tex = load_texture_or_none("assets/coin.png")
        if tex:
            self.texture = tex

    def update(self, delta_time: float):
        self.center_x -= config.OBSTACLE_SPEED * config.GAME_SPEED_MULTIPLIER * delta_time
        if self.right < 0:
            self.remove_from_sprite_lists()
