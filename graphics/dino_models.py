import arcade


class DinoModels:
    def __init__(self):
        self.run = arcade.SpriteSolidColor(40, 40, arcade.color.WHITE)
        self.jump = arcade.SpriteSolidColor(40, 40, arcade.color.YELLOW)
        self.crouch = arcade.SpriteSolidColor(40, 25, arcade.color.ORANGE)

        # потом:
        # self.run = arcade.Sprite("assets/dino/run.png", scale=...)
        # self.jump = arcade.Sprite("assets/dino/jump.png", scale=...)
        # self.crouch = arcade.Sprite("assets/dino/crouch.png")
