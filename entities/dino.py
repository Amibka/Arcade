import arcade
from config import DINO_SIZE, GROUND_Y
from graphics.dino_models import DinoModels


class Dino(arcade.SpriteSolidColor):
    def __init__(self, x: float):
        super().__init__(DINO_SIZE, DINO_SIZE, arcade.color.WHITE)

        self.models = DinoModels()
        self.current_sprite = self.models.run

        self.center_x = x
        self.center_y = GROUND_Y

        self.velocity_y = 0.0
        self.on_ground = True

    def jump(self, jump_velocity: float) -> None:
        if self.on_ground:
            self.velocity_y = jump_velocity
            self.on_ground = False

    def update_sprite(self):
        if not self.on_ground:
            self.current_sprite = self.models.jump
        elif self.is_crouching:
            self.current_sprite = self.models.crouch
        else:
            self.current_sprite = self.models.run

        self.current_sprite.center_x = self.center_x
        self.current_sprite.center_y = self.center_y

