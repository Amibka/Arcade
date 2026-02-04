import config


class PhysicsEngine:
    """
    Простейший физический движок:
    - гравитация
    - вертикальная скорость
    """

    def __init__(self, dino):
        self.dino = dino

    def update(self, delta_time: float) -> None:
        # гравитация
        self.dino.velocity_y -= config.GRAVITY * delta_time
        self.dino.center_y += self.dino.velocity_y * delta_time

        # столкновение с землей
        if self.dino.center_y <= config.GROUND_Y:
            self.dino.center_y = config.GROUND_Y
            self.dino.velocity_y = 0
            self.dino.on_ground = True
