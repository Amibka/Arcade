import arcade
import config


class Background:
    def __init__(self):
        self.sprite = arcade.SpriteSolidColor(
            width=config.SCREEN_WIDTH,
            height=config.SCREEN_HEIGHT,
            color=arcade.color.DARK_SLATE_GRAY,
        )

        self.sprite.center_x = config.SCREEN_WIDTH // 2
        self.sprite.center_y = config.SCREEN_HEIGHT // 2

        # позже заменишь на:
        # arcade.Sprite("assets/background/background.png")

    def draw(self):
        self.sprite.draw()
