import arcade

import config
from graphics.assets import load_sprite_or_solid


class Background:
    def __init__(self):
        self.sprite = load_sprite_or_solid(
            "assets/background/background.png",
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY,
        )

        self.sprite.center_x = config.SCREEN_WIDTH // 2
        self.sprite.center_y = config.SCREEN_HEIGHT // 2

    def draw(self, day_time=0.0, enable_day_night=True):
        arcade.draw_sprite(self.sprite)
