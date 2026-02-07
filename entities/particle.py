import random
import arcade
from typing import Tuple


class Particle(arcade.SpriteSolidColor):
    def __init__(
        self,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        life: float,
        velocity_x: float,
        velocity_y: float,
        center_x: float,
        center_y: float,
        fade: bool = True,
        alpha: int = 255,
    ):
        super().__init__(
            width, height, center_x=center_x, center_y=center_y, color=color
        )
        self.life = life
        self.start_life = life
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.fade = fade
        self.alpha = alpha

    def update(self, delta_time: float):
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time

        self.life -= delta_time
        if self.fade and self.start_life > 0:
            t = max(self.life / self.start_life, 0.0)
            self.alpha = int(255 * t)

        if self.life <= 0:
            self.remove_from_sprite_lists()


def make_dust_particle(x: float, y: float) -> Particle:
    size = random.randint(4, 8)
    vx = random.uniform(-40, -10)
    vy = random.uniform(10, 40)
    return Particle(
        size,
        size,
        arcade.color.BLACK,
        life=0.5,
        velocity_x=vx,
        velocity_y=vy,
        center_x=x,
        center_y=y,
    )


def make_land_particle(x: float, y: float) -> Particle:
    size = random.randint(6, 12)
    vx = random.uniform(-80, 60)
    vy = random.uniform(20, 80)
    return Particle(
        size,
        size,
        arcade.color.BLACK,
        life=0.7,
        velocity_x=vx,
        velocity_y=vy,
        center_x=x,
        center_y=y,
    )


def make_wind_particle(x: float, y: float, direction: int) -> Particle:
    width = random.randint(28, 46)
    height = random.randint(4, 6)
    vx = direction * random.uniform(160, 240)
    vy = random.uniform(-10, 10)
    return Particle(
        width,
        height,
        arcade.color.BLACK,
        life=0.8,
        velocity_x=vx,
        velocity_y=vy,
        center_x=x,
        center_y=y,
        fade=True,
        alpha=220,
    )
