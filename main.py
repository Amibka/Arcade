import arcade
from arcade.camera import Camera2D
import config

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    DINO_JUMP_VELOCITY,
    SPAWN_INTERVAL,
    DEV_MODE,
    DEBUG_TEXT_COLOR,
)

from entities.dino import Dino
from entities.obstacle import Obstacle

from physics import PhysicsEngine
from rules import Rule, RuleManager

from graphics.background import Background


class Game(arcade.Window):
    def __init__(self):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
        )
        arcade.set_background_color(arcade.color.BLACK)
        self.background = Background()
        # sprites
        self.dino_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()

        self.dino = Dino(x=100)
        self.dino_list.append(self.dino)

        # physics engine
        self.physics_engine = PhysicsEngine(self.dino)

        self.camera = Camera2D()

        # rule system
        self.rule_text = ""
        self.rule_text_timer = 0.0

        self.rule_manager = RuleManager(
            rules=[
                Rule(
                    "LOW GRAVITY",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_LOW,
                        speed=config.OBSTACLE_SPEED_NORMAL,
                    ),
                ),
                Rule(
                    "HIGH GRAVITY",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_HIGH,
                        speed=config.OBSTACLE_SPEED_NORMAL,
                    ),
                ),
                Rule(
                    "FAST WORLD",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_FAST,
                    ),
                ),
                Rule(
                    "SLOW WORLD",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_SLOW,
                    ),
                ),
            ],
            interval=config.RULE_CHANGE_INTERVAL,
        )

        # game state
        self.spawn_timer = 0.0
        self.score = 0.0
        self.game_over = False
        self.jump_multiplier = 1.0

    def reset_game(self) -> None:
        self.dino_list.clear()
        self.obstacle_list.clear()

        self.dino = Dino(x=100)
        self.dino_list.append(self.dino)

        self.physics_engine = PhysicsEngine(self.dino)

        self.spawn_timer = 0.0
        self.score = 0.0
        self.game_over = False
        self.jump_multiplier = 1.0

    def set_physics(self, gravity: int, speed: int) -> None:
        config.GRAVITY = gravity
        config.OBSTACLE_SPEED = speed

        raw_multiplier = config.GRAVITY_NORMAL / gravity
        self.jump_multiplier = max(0.85, min(raw_multiplier, 1.15))

        # выбор максимальной высоты прыжка
        if gravity == config.GRAVITY_HIGH:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_HIGH
        elif gravity == config.GRAVITY_LOW:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_LOW
        else:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_NORMAL

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and not self.game_over:
            jump_velocity = DINO_JUMP_VELOCITY * self.jump_multiplier
            self.dino.jump(jump_velocity)

        if key == arcade.key.R and self.game_over:
            self.reset_game()

        if DEV_MODE:
            if key == arcade.key.F1:
                self.rule_manager.toggle_freeze()

            if key == arcade.key.F2:
                if self.rule_manager.force_next_rule():
                    if self.rule_manager.current_rule:
                        self.rule_text = self.rule_manager.current_rule.name
                        self.rule_text_timer = 2.0

    def on_update(self, delta_time: float):
        if self.game_over:
            return

        # physics
        self.physics_engine.update(delta_time)

        # score & spawn
        self.score += delta_time
        self.spawn_timer += delta_time

        if self.spawn_timer >= SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            self.obstacle_list.append(Obstacle())

        # sprite updates
        self.dino_list.update(delta_time)
        self.obstacle_list.update(delta_time)

        # rules update
        if self.rule_manager.update(delta_time):
            if self.rule_manager.current_rule:
                self.rule_text = self.rule_manager.current_rule.name
                self.rule_text_timer = 2.0

        if self.rule_text_timer > 0:
            self.rule_text_timer -= delta_time

        # collision
        if arcade.check_for_collision_with_list(
            self.dino,
            self.obstacle_list,
        ):
            self.game_over = True

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.camera.use()

        self.dino_list.draw()
        self.obstacle_list.draw()

        # score
        arcade.draw_text(
            f"Score: {int(self.score)}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16,
        )

        # rule info
        if self.rule_text_timer > 0:
            arcade.draw_text(
                f"RULE: {self.rule_text}",
                SCREEN_WIDTH // 2 - 120,
                SCREEN_HEIGHT - 60,
                arcade.color.YELLOW,
                18,
            )

        # game over
        if self.game_over:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH // 2 - 80,
                SCREEN_HEIGHT // 2,
                arcade.color.RED,
                24,
            )
            arcade.draw_text(
                "Press R to restart",
                SCREEN_WIDTH // 2 - 110,
                SCREEN_HEIGHT // 2 - 40,
                arcade.color.WHITE,
                14,
            )

        # dev overlay
        if DEV_MODE:
            arcade.draw_text(
                f"y={int(self.dino.center_y)} vy={int(self.dino.velocity_y)}",
                10,
                10,
                DEBUG_TEXT_COLOR,
                12,
            )
            arcade.draw_text(
                f"Obstacles: {len(self.obstacle_list)}",
                10,
                26,
                DEBUG_TEXT_COLOR,
                12,
            )
            arcade.draw_text(
                f"Spawn timer: {self.spawn_timer:.2f}",
                10,
                42,
                DEBUG_TEXT_COLOR,
                12,
            )
            arcade.draw_text(
                "F1: pause rules | F2: next rule",
                10,
                58,
                DEBUG_TEXT_COLOR,
                12,
            )


def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
