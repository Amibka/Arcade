import config


class PhysicsEngine:
    def __init__(self, dino):
        self.dino = dino

    def update(self, delta_time: float) -> None:
        if hasattr(self.dino, "jump_buffer_left"):
            self.dino.jump_buffer_left = max(
                self.dino.jump_buffer_left - delta_time, 0.0
            )
        if hasattr(self.dino, "coyote_time_left"):
            self.dino.coyote_time_left = max(
                self.dino.coyote_time_left - delta_time, 0.0
            )
        self.dino.velocity_y -= config.GRAVITY * delta_time
        if self.dino.velocity_y < 0:
            self.dino.velocity_y += (
                -self.dino.velocity_y * config.AIR_DRAG * delta_time
            )
        if self.dino.velocity_y < -config.TERMINAL_VELOCITY:
            self.dino.velocity_y = -config.TERMINAL_VELOCITY
        self.dino.center_y += self.dino.velocity_y * delta_time

        if self.dino.bottom <= config.GROUND_Y:
            self.dino.bottom = config.GROUND_Y
            self.dino.velocity_y = 0
            self.dino.on_ground = True
            if hasattr(self.dino, "jump_count"):
                self.dino.jump_count = 0
            if hasattr(self.dino, "coyote_time_left"):
                self.dino.coyote_time_left = config.COYOTE_TIME
        if hasattr(self.dino, "try_consume_jump"):
            self.dino.try_consume_jump()
