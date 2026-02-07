import arcade
import config
from graphics.assets import load_texture_or_none


POWERUP_COLORS = {
    "turbo": arcade.color.ORANGE,
    "shield": arcade.color.CYAN,
    "double_jump": arcade.color.MAGENTA,
}


class PowerUp(arcade.SpriteSolidColor):
    def __init__(self, kind: str, x: float, y: float):
        color = POWERUP_COLORS.get(kind, arcade.color.WHITE)
        super().__init__(24, 24, center_x=x, center_y=y, color=color)
        self.kind = kind
        tex = load_texture_or_none(f"assets/powerups/{kind}.png")
        if tex:
            self.texture = tex

    def update(self, delta_time: float):
        self.center_x -= config.OBSTACLE_SPEED * config.GAME_SPEED_MULTIPLIER * delta_time
        if self.right < 0:
            self.remove_from_sprite_lists()
