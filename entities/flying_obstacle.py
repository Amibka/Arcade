import random
import arcade
import config
from graphics.assets import load_texture_or_none, load_texture_sequence


class FlyingObstacle(arcade.SpriteSolidColor):
    def __init__(self, height_type: str):
        super().__init__(
            width=50,
            height=30,
            color=arcade.color.WHITE,
        )
        self.anim_timer = 0.0
        self.anim_index = 0
        self.textures = load_texture_sequence("assets/obstacles/bird", max_frames=6)
        if not self.textures:
            single = load_texture_or_none("assets/obstacles/bird.png")
            if single:
                self.textures = [single]
        if self.textures:
            self.texture = self.textures[0]

        self.center_x = config.SCREEN_WIDTH + 50

        if height_type == "low":
            self.center_y = config.BIRD_HEIGHT_LOW
        else:
            self.center_y = config.BIRD_HEIGHT_HIGH

    def update(self, delta_time: float):
        if self.textures and len(self.textures) > 1:
            self.anim_timer += delta_time
            if self.anim_timer >= 0.12:
                self.anim_timer = 0.0
                self.anim_index = (self.anim_index + 1) % len(self.textures)
                self.texture = self.textures[self.anim_index]
        self.center_x -= config.OBSTACLE_SPEED * config.GAME_SPEED_MULTIPLIER * delta_time

        if self.right < 0:
            self.remove_from_sprite_lists()
