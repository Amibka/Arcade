import arcade
from config import (
    DINO_STAND_WIDTH,
    DINO_STAND_HEIGHT,
    DINO_CROUCH_HEIGHT,
    DINO_CROUCH_WIDTH,
    GROUND_Y,
    JUMP_BUFFER_TIME,
    JUMP_CUTOFF_MULT,
)
from graphics.dino_models import DinoModels


class Dino(arcade.SpriteSolidColor):
    def __init__(self, x: float):
        super().__init__(DINO_STAND_WIDTH, DINO_STAND_HEIGHT, arcade.color.BLACK)

        self.stand_width = DINO_STAND_WIDTH
        self.stand_height = DINO_STAND_HEIGHT
        self.crouch_width = DINO_CROUCH_WIDTH
        self.crouch_height = DINO_CROUCH_HEIGHT

        self.models = DinoModels()
        self.current_texture = None
        self.anim_timer = 0.0
        self.anim_index = 0

        self.center_x = x
        self.center_y = GROUND_Y
        self.bottom = GROUND_Y

        self.velocity_y = 0.0
        self.on_ground = True
        self.is_crouching = False
        self.jump_count = 0
        self.max_jumps = 1
        self.jump_buffer_left = 0.0
        self.coyote_time_left = 0.0
        self.pending_jump_velocity = 0.0

    def request_jump(self, jump_velocity: float) -> None:
        self.jump_buffer_left = JUMP_BUFFER_TIME
        self.pending_jump_velocity = jump_velocity

    def try_consume_jump(self) -> None:
        if self.jump_buffer_left <= 0.0:
            return
        can_jump = self.on_ground or self.jump_count < self.max_jumps or self.coyote_time_left > 0.0
        if not can_jump:
            return
        self.velocity_y = self.pending_jump_velocity
        self.on_ground = False
        self.jump_count += 1
        self.jump_buffer_left = 0.0
        self.coyote_time_left = 0.0

    def cut_jump(self) -> None:
        if self.velocity_y > 0:
            self.velocity_y *= JUMP_CUTOFF_MULT

    def update(self, delta_time: float):
        self.update_sprite(delta_time)

    def update_sprite(self, delta_time: float) -> None:
        self.apply_crouch_state()

        if not self.on_ground:
            self.current_texture = self.models.jump_texture
        elif self.is_crouching:
            self.current_texture = self.models.crouch_texture
        else:
            self.current_texture = self.get_run_texture(delta_time)

    def apply_crouch_state(self) -> None:
        prev_center_y = self.center_y
        if self.is_crouching and self.on_ground:
            self.width = self.crouch_width
            self.height = self.crouch_height
        else:
            self.width = self.stand_width
            self.height = self.stand_height
        if self.on_ground:
            self.bottom = GROUND_Y
        else:
            self.center_y = prev_center_y

    def get_run_texture(self, delta_time: float):
        if not self.models.run_textures:
            return None
        if len(self.models.run_textures) == 1:
            return self.models.run_textures[0]
        self.anim_timer += delta_time
        if self.anim_timer >= 0.12:
            self.anim_timer = 0.0
            self.anim_index = (self.anim_index + 1) % len(self.models.run_textures)
        return self.models.run_textures[self.anim_index]

    def draw(self):
        if self.current_texture:
            arcade.draw_texture_rectangle(
                self.center_x, self.center_y, self.width, self.height, self.current_texture
            )
        else:
            arcade.draw_sprite(self)
