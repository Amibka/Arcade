import arcade
import math
import random
from arcade.camera import Camera2D

import config
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEV_MODE,
    DEBUG_TEXT_COLOR,
)

from entities.dino import Dino
from entities.obstacle import Obstacle
from entities.flying_obstacle import FlyingObstacle
from entities.particle import make_dust_particle, make_land_particle, make_wind_particle
from entities.coin import Coin
from entities.powerup import PowerUp
from entities.meteor import Meteor
from physics import PhysicsEngine
from rules import Rule, RuleManager
from graphics.assets import load_texture_or_none, resource_path
from systems import storage


def load_sound_or_none(path: str):
    try:
        return arcade.load_sound(resource_path(path))
    except Exception:
        return None


class Button:
    def __init__(self, text, x, y, w, h, action, color, texture=None):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.action = action
        self.color = color
        self.texture = texture

    def hit_test(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h

    def draw(self):
        arcade.draw_lbwh_rectangle_outline(
            self.x,
            self.y,
            self.w,
            self.h,
            arcade.color.BLACK,
            2,
        )
        if self.texture:
            arcade.draw_texture_rectangle(
                self.x + self.w / 2,
                self.y + self.h / 2,
                self.w - 8,
                self.h - 8,
                self.texture,
            )
        arcade.draw_text(
            self.text,
            self.x + self.w / 2,
            self.y + self.h / 2 - 8,
            arcade.color.BLACK,
            16,
            anchor_x="center",
        )


class AppContext:
    def __init__(self):
        storage.init_db()
        self.refresh_stats()
        self.enable_wind = storage.get_setting("enable_wind", "1") == "1"
        self.enable_day_night = storage.get_setting("enable_day_night", "1") == "1"
        self.enable_events = storage.get_setting("enable_events", "1") == "1"
        self.enable_meteors = storage.get_setting("enable_meteors", "1") == "1"
        self.enable_golden = storage.get_setting("enable_golden", "1") == "1"
        self.enable_sound = storage.get_setting("enable_sound", "1") == "1"

    def refresh_stats(self):
        self.stats = storage.get_stats()

    def set_setting(self, key, value):
        storage.set_setting(key, "1" if value else "0")


class MainMenuView(arcade.View):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.buttons = []
        self.secret_code = [
            arcade.key.UP,
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.DOWN,
            arcade.key.LEFT,
            arcade.key.RIGHT,
            arcade.key.LEFT,
            arcade.key.RIGHT,
        ]
        self.secret_index = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        w, h = 260, 50
        x = SCREEN_WIDTH / 2 - w / 2
        start_y = SCREEN_HEIGHT / 2 + 60
        gap = 14

        self.buttons.append(
            Button("PLAY", x, start_y, w, h, self.start_game, arcade.color.WHITE)
        )
        self.buttons.append(
            Button(
                "SHOP",
                x,
                start_y - (h + gap),
                w,
                h,
                self.open_shop,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "SETTINGS",
                x,
                start_y - 2 * (h + gap),
                w,
                h,
                self.open_settings,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "EXIT",
                x,
                start_y - 3 * (h + gap),
                w,
                h,
                self.exit_game,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "RESET STATS",
                x,
                start_y - 4 * (h + gap),
                w,
                h,
                self.reset_stats,
                arcade.color.WHITE,
            )
        )

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "DINO: CHANGE RULES",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 120,
            arcade.color.BLACK,
            32,
            anchor_x="center",
        )

        stats = self.app.stats
        arcade.draw_text(
            f"Best Score: {int(stats['best_score'])}",
            40,
            SCREEN_HEIGHT - 60,
            arcade.color.BLACK,
            16,
        )
        arcade.draw_text(
            f"Total Runs: {stats['total_runs']}",
            40,
            SCREEN_HEIGHT - 82,
            arcade.color.BLACK,
            16,
        )
        arcade.draw_text(
            f"Total Coins: {stats['total_coins']}",
            40,
            SCREEN_HEIGHT - 104,
            arcade.color.BLACK,
            16,
        )
        arcade.draw_text(
            f"Coins Balance: {stats['coins_balance']}",
            40,
            SCREEN_HEIGHT - 126,
            arcade.color.BLACK,
            16,
        )

        for btn in self.buttons:
            btn.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.action()
                return

    def on_key_press(self, key, modifiers):
        if key == self.secret_code[self.secret_index]:
            self.secret_index += 1
            if self.secret_index >= len(self.secret_code):
                self.secret_index = 0
                self.window.show_view(DevRoomView(self.app))
        else:
            self.secret_index = 0

    def start_game(self):
        self.window.show_view(GameView(self.app))

    def open_shop(self):
        self.window.show_view(ShopView(self.app))

    def open_settings(self):
        self.window.show_view(SettingsView(self.app))

    def exit_game(self):
        self.window.close()

    def reset_stats(self):
        storage.reset_all()
        self.app.refresh_stats()


class ShopView(arcade.View):
    ITEMS = [
        {"id": "coin_boost", "name": "Coin Booster (+50%)", "cost": 120},
        {"id": "score_boost", "name": "Score Boost (+10%)", "cost": 150},
        {"id": "turbo_plus", "name": "Turbo+ (x1.5)", "cost": 120},
        {"id": "start_shield", "name": "Start Shield (3s)", "cost": 200},
        {"id": "secret_guide", "name": "Secret Guide", "cost": 100},
    ]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.buttons = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.build_buttons()
        self.shop_tip = random.choice(
            [
                "Tip: Boosts stack well.",
                "Sale: The prices are made up!",
                "Warning: Do not feed the cactus.",
                "Pro tip: Turbo goes brrrr.",
                "Rare find: Smiling costs 0 coins.",
            ]
        )

    def build_buttons(self):
        self.buttons = []
        w, h = 420, 44
        x = SCREEN_WIDTH / 2 - w / 2
        start_y = SCREEN_HEIGHT / 2 + 80
        gap = 12

        for idx, item in enumerate(self.ITEMS):
            y = start_y - idx * (h + gap)
            self.buttons.append(
                Button(
                    f"{item['name']} - {item['cost']}",
                    x,
                    y,
                    w,
                    h,
                    lambda i=item: self.try_buy(i),
                    arcade.color.WHITE,
                )
            )

        self.buttons.append(
            Button(
                "BACK",
                30,
                30,
                140,
                40,
                self.go_back,
                arcade.color.WHITE,
            )
        )

    def try_buy(self, item):
        if storage.is_owned(item["id"]):
            return
        if storage.purchase(item["id"], item["cost"]):
            self.app.refresh_stats()

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "SHOP",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 80,
            arcade.color.BLACK,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            self.shop_tip,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 110,
            arcade.color.BLACK,
            14,
            anchor_x="center",
        )

        balance = self.app.stats["coins_balance"]
        arcade.draw_text(
            f"Coins Balance: {balance}",
            40,
            SCREEN_HEIGHT - 50,
            arcade.color.BLACK,
            16,
        )

        for btn in self.buttons:
            btn.draw()

        y = SCREEN_HEIGHT / 2 - 80
        for item in self.ITEMS:
            owned = storage.is_owned(item["id"])
            status = "OWNED" if owned else "LOCKED"
            arcade.draw_text(
                f"{item['name']}: {status}",
                40,
                y,
                arcade.color.BLACK,
                14,
            )
            y -= 22
        arcade.draw_text(
            "No refunds. Ever.",
            SCREEN_WIDTH - 220,
            40,
            arcade.color.BLACK,
            12,
        )
        if storage.is_owned("secret_guide"):
            arcade.draw_text(
                "Secrets: ↑↑↓↓←→←→ in menu | 100-coin streak = GOLDEN | Meteor = +50",
                SCREEN_WIDTH / 2,
                60,
                arcade.color.BLACK,
                12,
                anchor_x="center",
            )

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.action()
                return

    def go_back(self):
        self.window.show_view(MainMenuView(self.app))


class SettingsView(arcade.View):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.buttons = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        w, h = 360, 44
        x = SCREEN_WIDTH / 2 - w / 2
        start_y = SCREEN_HEIGHT / 2 + 40
        gap = 12

        self.buttons.append(
            Button(
                f"Wind: {'ON' if self.app.enable_wind else 'OFF'}",
                x,
                start_y,
                w,
                h,
                self.toggle_wind,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Day/Night: {'ON' if self.app.enable_day_night else 'OFF'}",
                x,
                start_y - (h + gap),
                w,
                h,
                self.toggle_day_night,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Events: {'ON' if self.app.enable_events else 'OFF'}",
                x,
                start_y - 2 * (h + gap),
                w,
                h,
                self.toggle_events,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Meteors: {'ON' if self.app.enable_meteors else 'OFF'}",
                x,
                start_y - 3 * (h + gap),
                w,
                h,
                self.toggle_meteors,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Golden: {'ON' if self.app.enable_golden else 'OFF'}",
                x,
                start_y - 4 * (h + gap),
                w,
                h,
                self.toggle_golden,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Sound: {'ON' if self.app.enable_sound else 'OFF'}",
                x,
                start_y - 5 * (h + gap),
                w,
                h,
                self.toggle_sound,
                arcade.color.WHITE,
            )
        )

        self.buttons.append(
            Button(
                "BACK",
                30,
                30,
                140,
                40,
                self.go_back,
                arcade.color.WHITE,
            )
        )

    def toggle_wind(self):
        self.app.enable_wind = not self.app.enable_wind
        self.app.set_setting("enable_wind", self.app.enable_wind)
        self.build_buttons()

    def toggle_day_night(self):
        self.app.enable_day_night = not self.app.enable_day_night
        self.app.set_setting("enable_day_night", self.app.enable_day_night)
        self.build_buttons()

    def toggle_events(self):
        self.app.enable_events = not self.app.enable_events
        self.app.set_setting("enable_events", self.app.enable_events)
        self.build_buttons()

    def toggle_meteors(self):
        self.app.enable_meteors = not self.app.enable_meteors
        self.app.set_setting("enable_meteors", self.app.enable_meteors)
        self.build_buttons()

    def toggle_golden(self):
        self.app.enable_golden = not self.app.enable_golden
        self.app.set_setting("enable_golden", self.app.enable_golden)
        self.build_buttons()

    def toggle_sound(self):
        self.app.enable_sound = not self.app.enable_sound
        self.app.set_setting("enable_sound", self.app.enable_sound)
        self.build_buttons()
    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "SETTINGS",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 80,
            arcade.color.BLACK,
            28,
            anchor_x="center",
        )
        for btn in self.buttons:
            btn.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.action()
                return

    def go_back(self):
        self.window.show_view(MainMenuView(self.app))


class DevRoomView(arcade.View):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.buttons = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        w, h = 420, 44
        x = SCREEN_WIDTH / 2 - w / 2
        start_y = SCREEN_HEIGHT / 2 + 120
        gap = 12

        self.buttons.append(
            Button(
                f"Events: {'ON' if self.app.enable_events else 'OFF'}",
                x,
                start_y,
                w,
                h,
                self.toggle_events,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Meteors: {'ON' if self.app.enable_meteors else 'OFF'}",
                x,
                start_y - (h + gap),
                w,
                h,
                self.toggle_meteors,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Golden Streak: {'ON' if self.app.enable_golden else 'OFF'}",
                x,
                start_y - 2 * (h + gap),
                w,
                h,
                self.toggle_golden,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Wind: {'ON' if self.app.enable_wind else 'OFF'}",
                x,
                start_y - 3 * (h + gap),
                w,
                h,
                self.toggle_wind,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                f"Day/Night: {'ON' if self.app.enable_day_night else 'OFF'}",
                x,
                start_y - 4 * (h + gap),
                w,
                h,
                self.toggle_day_night,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "+100 Coins",
                x,
                start_y - 5 * (h + gap),
                w,
                h,
                self.add_100_coins,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "+1000 Coins",
                x,
                start_y - 6 * (h + gap),
                w,
                h,
                self.add_1000_coins,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "Unlock All Shop Items",
                x,
                start_y - 7 * (h + gap),
                w,
                h,
                self.unlock_all_items,
                arcade.color.WHITE,
            )
        )
        self.buttons.append(
            Button(
                "BACK",
                30,
                30,
                140,
                40,
                self.go_back,
                arcade.color.WHITE,
            )
        )

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "DEV ROOM",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 80,
            arcade.color.BLACK,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            "Cheat Menu",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 120,
            arcade.color.BLACK,
            16,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Coins Balance: {self.app.stats['coins_balance']}",
            40,
            SCREEN_HEIGHT - 150,
            arcade.color.BLACK,
            14,
        )
        for btn in self.buttons:
            btn.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.action()
                return

    def toggle_events(self):
        self.app.enable_events = not self.app.enable_events
        self.app.set_setting("enable_events", self.app.enable_events)
        self.build_buttons()

    def toggle_meteors(self):
        self.app.enable_meteors = not self.app.enable_meteors
        self.app.set_setting("enable_meteors", self.app.enable_meteors)
        self.build_buttons()

    def toggle_golden(self):
        self.app.enable_golden = not self.app.enable_golden
        self.app.set_setting("enable_golden", self.app.enable_golden)
        self.build_buttons()

    def toggle_wind(self):
        self.app.enable_wind = not self.app.enable_wind
        self.app.set_setting("enable_wind", self.app.enable_wind)
        self.build_buttons()

    def toggle_day_night(self):
        self.app.enable_day_night = not self.app.enable_day_night
        self.app.set_setting("enable_day_night", self.app.enable_day_night)
        self.build_buttons()

    def add_100_coins(self):
        storage.add_coins(100)
        self.app.refresh_stats()

    def add_1000_coins(self):
        storage.add_coins(1000)
        self.app.refresh_stats()

    def unlock_all_items(self):
        storage.unlock_items([item["id"] for item in ShopView.ITEMS])
        self.app.refresh_stats()

    def go_back(self):
        self.window.show_view(MainMenuView(self.app))


class GameOverView(arcade.View):
    def __init__(self, app, score: float, coins: int):
        super().__init__()
        self.app = app
        self.score = int(score)
        self.coins = int(coins)
        self.buttons = []

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        w, h = 260, 50
        x = SCREEN_WIDTH / 2 - w / 2
        y = SCREEN_HEIGHT / 2 - 140
        gap = 14
        self.buttons.append(
            Button("RESTART", x, y, w, h, self.restart, arcade.color.WHITE)
        )
        self.buttons.append(
            Button("MENU", x, y - (h + gap), w, h, self.menu, arcade.color.WHITE)
        )

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "GAME OVER",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 160,
            arcade.color.BLACK,
            32,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Score: {self.score}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 80,
            arcade.color.BLACK,
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Coins: {self.coins}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            arcade.color.BLACK,
            18,
            anchor_x="center",
        )
        stats = self.app.stats
        arcade.draw_text(
            f"Best Score: {int(stats['best_score'])}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 20,
            arcade.color.BLACK,
            16,
            anchor_x="center",
        )
        for btn in self.buttons:
            btn.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.hit_test(x, y):
                btn.action()
                return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.restart()
        if key == arcade.key.M:
            self.menu()

    def restart(self):
        self.window.show_view(GameView(self.app))

    def menu(self):
        self.window.show_view(MainMenuView(self.app))


class GameView(arcade.View):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.camera = Camera2D()
        self.stats_recorded = False
        self.load_sounds()
        self.reset_game()
        self.setup_rules()

    def setup_rules(self):
        self.rule_manager = RuleManager(
            rules=[
                Rule(
                    "NOTHING",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_NORMAL,
                    ),
                ),
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
                Rule(
                    "DOUBLE JUMP",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_NORMAL,
                        double_jump=True,
                    ),
                ),
                Rule(
                    "SLIPPERY FLOOR",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_NORMAL,
                        slippery=True,
                    ),
                ),
            ],
            combo_rules=[
                Rule(
                    "FAST + LOW",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_LOW,
                        speed=config.OBSTACLE_SPEED_FAST,
                    ),
                ),
                Rule(
                    "SLOW + LOW",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_LOW,
                        speed=config.OBSTACLE_SPEED_SLOW,
                    ),
                ),
                Rule(
                    "FAST + DOUBLE",
                    lambda: self.set_physics(
                        gravity=config.GRAVITY_NORMAL,
                        speed=config.OBSTACLE_SPEED_FAST,
                        double_jump=True,
                    ),
                ),
            ],
            combo_chance=config.RULE_COMBO_CHANCE,
            interval=config.RULE_CHANGE_INTERVAL,
        )

        if self.rule_manager.force_next_rule():
            if self.rule_manager.current_rule:
                self.rule_text = self.rule_manager.current_rule.name
                self.rule_text_timer = 2.0

    def reset_game(self):
        self.dino_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()
        self.particle_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()
        self.meteor_list = arcade.SpriteList()

        self.dino = Dino(x=100)
        self.dino_list.append(self.dino)
        self.physics_engine = PhysicsEngine(self.dino)

        self.rule_text = ""
        self.rule_text_timer = 0.0
        self.spawn_timer = 0.0
        self.last_obstacle_tag = None
        self.score = 0.0
        self.level = 1
        self.level_text_timer = 0.0
        self.level_speed_mult = 1.0
        self.level_color_index = 0
        self.coins = 0
        self.game_over = False
        self.jump_multiplier = 1.0
        self.particle_timer = 0.0
        self.footstep_left = True
        self.move_dir = 0
        self.player_vel_x = 0.0
        self.day_time = 0.0
        self.difficulty_time = 0.0
        self.wind_timer = 0.0
        self.wind_time_left = 0.0
        self.wind_dir = 0
        self.wind_particle_timer = 0.0
        self.coin_timer = 0.0
        self.powerup_timer = 0.0
        self.meteor_timer = 0.0
        self.turbo_time_left = 0.0
        self.shield_time_left = 0.0
        self.double_jump_time_left = 0.0
        self.slippery_active = False
        self.rule_double_jump = False
        self.rule_stack = 0
        self.stats_recorded = False
        self.paused = False
        self.difficulty_t = 0.0
        self.crouch_held = False
        self.coin_streak = 0
        self.golden_time_left = 0.0
        self.event_timer = 0.0
        self.event_time_left = 0.0
        self.active_event = None
        self.next_event_time = random.uniform(
            config.EVENT_INTERVAL_MIN, config.EVENT_INTERVAL_MAX
        )
        if storage.is_owned("start_shield"):
            self.shield_time_left = 3.0

        min_spawn, max_spawn = self.get_spawn_interval_range()
        self.next_spawn_time = random.uniform(min_spawn, max_spawn)

    def load_sounds(self):
        self.snd_jump = load_sound_or_none("assets/sfx/jump.wav")
        self.snd_coin = load_sound_or_none("assets/sfx/coin.wav")
        self.snd_powerup = load_sound_or_none("assets/sfx/powerup.wav")
        self.snd_hit = load_sound_or_none("assets/sfx/hit.wav")
        self.snd_level = load_sound_or_none("assets/sfx/level_up.wav")

    def play_sfx(self, sound):
        if sound and self.app.enable_sound:
            arcade.play_sound(sound)

    def update_level(self):
        if config.LEVEL_SCORE_STEP <= 0:
            return
        new_level = min(config.LEVEL_MAX, int(self.score // config.LEVEL_SCORE_STEP) + 1)
        if new_level != self.level:
            self.level = new_level
            self.level_text_timer = 2.0
            self.level_speed_mult = 1.0 + (self.level - 1) * config.LEVEL_SPEED_STEP
            self.level_color_index = max(0, min(self.level - 1, len(config.LEVEL_DAY_COLORS) - 1))
            self.play_sfx(self.snd_level)

    def set_physics(self, gravity, speed, double_jump=False, slippery=False):
        config.GRAVITY = gravity
        config.OBSTACLE_SPEED = speed

        raw_multiplier = math.sqrt(config.GRAVITY_NORMAL / gravity)
        self.jump_multiplier = max(0.7, min(raw_multiplier, 1.35))

        self.rule_double_jump = double_jump
        self.slippery_active = slippery

        if gravity == config.GRAVITY_HIGH:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_HIGH
        elif gravity == config.GRAVITY_LOW:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_LOW
        else:
            config.MAX_JUMP_HEIGHT = config.MAX_JUMP_HEIGHT_NORMAL

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
            return

        if self.paused:
            return

        if key in (arcade.key.SPACE, arcade.key.W) and not self.game_over:
            base_gravity = config.GRAVITY_NORMAL
            jump_velocity = (
                base_gravity * config.JUMP_TIME_TO_APEX * self.jump_multiplier
            )
            if hasattr(self.dino, "request_jump"):
                self.dino.request_jump(jump_velocity)
            else:
                self.dino.jump(jump_velocity)
            self.play_sfx(self.snd_jump)

        if key == arcade.key.R and self.game_over:
            self.reset_game()
            self.setup_rules()

        if key == arcade.key.M and self.game_over:
            self.window.show_view(MainMenuView(self.app))

        if key == arcade.key.S and not self.game_over:
            self.crouch_held = True

        if key == arcade.key.A:
            self.move_dir = -1
        elif key == arcade.key.D:
            self.move_dir = 1

        if DEV_MODE:
            if key == arcade.key.F1:
                self.rule_manager.toggle_freeze()
            if key == arcade.key.F2:
                if self.rule_manager.force_next_rule():
                    if self.rule_manager.current_rule:
                        self.rule_text = self.rule_manager.current_rule.name
                        self.rule_text_timer = 2.0

    def on_key_release(self, key, modifiers):
        if key == arcade.key.S:
            self.crouch_held = False
        if key in (arcade.key.SPACE, arcade.key.W):
            if hasattr(self.dino, "cut_jump"):
                self.dino.cut_jump()

        if key == arcade.key.A and self.move_dir == -1:
            self.move_dir = 0
        elif key == arcade.key.D and self.move_dir == 1:
            self.move_dir = 0

    def on_update(self, delta_time):
        if self.paused:
            return
        if self.game_over:
            return

        was_on_ground = self.dino.on_ground
        self.physics_engine.update(delta_time)
        self.dino.is_crouching = self.crouch_held and self.dino.on_ground
        if not was_on_ground and self.dino.on_ground:
            self.spawn_land_burst()

        if self.app.enable_day_night:
            self.day_time += delta_time

        self.difficulty_time += delta_time
        self.difficulty_t = min(
            self.difficulty_time / max(config.DIFFICULTY_RAMP_DURATION, 1.0), 1.0
        )

        if self.app.enable_wind or self.active_event == "STORM":
            self.update_wind(delta_time)
        else:
            self.wind_time_left = 0.0
            self.wind_dir = 0

        self.update_powerups(delta_time)
        self.update_speed_multiplier()
        self.update_events(delta_time)

        if self.golden_time_left > 0:
            self.golden_time_left = max(0.0, self.golden_time_left - delta_time)
            self.dino.color = arcade.color.GOLD
        else:
            self.dino.color = arcade.color.BLACK

        self.score += delta_time * self.get_score_multiplier()
        self.update_level()
        if self.level_text_timer > 0:
            self.level_text_timer -= delta_time
        self.spawn_timer += delta_time
        self.coin_timer += delta_time
        self.powerup_timer += delta_time
        self.meteor_timer += delta_time

        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_timer = 0.0
            self.spawn_obstacle()
            min_spawn, max_spawn = self.get_spawn_interval_range()
            self.next_spawn_time = random.uniform(min_spawn, max_spawn)

        if self.coin_timer >= config.COIN_SPAWN_INTERVAL:
            self.coin_timer = 0.0
            coin_chance = config.COIN_SPAWN_CHANCE
            if self.active_event == "FEVER":
                coin_chance = min(1.0, coin_chance + config.FEVER_COIN_BONUS)
            if self.active_event == "DOUBLE COINS":
                coin_chance = min(1.0, coin_chance + 0.2)
            if random.random() < coin_chance:
                self.spawn_coin()

        if self.powerup_timer >= config.POWERUP_SPAWN_INTERVAL:
            self.powerup_timer = 0.0
            if random.random() < config.POWERUP_SPAWN_CHANCE:
                self.spawn_powerup()

        if self.app.enable_meteors and self.meteor_timer >= 1.5:
            self.meteor_timer = 0.0
            if random.random() < config.METEOR_SPAWN_CHANCE:
                self.spawn_meteor()

        self.update_player_movement(delta_time)
        if self.wind_time_left > 0:
            wind_force = config.WIND_FORCE
            if self.active_event == "STORM":
                wind_force *= config.STORM_WIND_FORCE_MULT
            self.dino.center_x += self.wind_dir * wind_force * delta_time
        self.dino.center_x = max(30, min(self.dino.center_x, SCREEN_WIDTH - 30))

        self.dino_list.update(delta_time)
        self.obstacle_list.update(delta_time)
        self.coin_list.update(delta_time)
        self.powerup_list.update(delta_time)
        self.meteor_list.update(delta_time)
        self.particle_list.update(delta_time)

        if self.rule_manager.update(delta_time):
            if self.rule_manager.current_rule:
                self.rule_text = self.rule_manager.current_rule.name
                self.rule_text_timer = 2.0
            self.rule_stack = min(config.RULE_STACK_MAX, self.rule_stack + 1)

        if self.rule_text_timer > 0:
            self.rule_text_timer -= delta_time

        if self.dino.on_ground:
            self.particle_timer += delta_time
            if self.particle_timer >= 0.05:
                self.particle_timer = 0.0
                self.spawn_run_dust()

        for coin in arcade.check_for_collision_with_list(self.dino, self.coin_list):
            coin.remove_from_sprite_lists()
            coin_mult = (
                config.DOUBLE_COIN_MULT if self.active_event == "DOUBLE COINS" else 1
            )
            if storage.is_owned("coin_boost"):
                coin_mult *= 1.5
            coin_gain = int(round(coin_mult))
            self.coins += coin_gain
            self.score += 2.0 * coin_mult
            self.coin_streak += 1
            self.play_sfx(self.snd_coin)
            if (
                self.app.enable_golden
                and self.coin_streak >= config.GOLDEN_STREAK_COINS
                and self.golden_time_left <= 0.0
            ):
                self.golden_time_left = config.GOLDEN_DURATION

        for powerup in arcade.check_for_collision_with_list(self.dino, self.powerup_list):
            powerup.remove_from_sprite_lists()
            self.apply_powerup(powerup.kind)
            self.play_sfx(self.snd_powerup)

        for meteor in arcade.check_for_collision_with_list(self.dino, self.meteor_list):
            meteor.remove_from_sprite_lists()
            self.score += config.METEOR_SCORE_BONUS

        hits = arcade.check_for_collision_with_list(self.dino, self.obstacle_list)
        if hits:
            if self.shield_time_left > 0:
                self.shield_time_left = 0.0
                for h in hits:
                    h.remove_from_sprite_lists()
            else:
                if not self.game_over:
                    self.game_over = True
                    self.record_stats_once()
                    self.play_sfx(self.snd_hit)
                    self.window.show_view(GameOverView(self.app, self.score, self.coins))
            self.coin_streak = 0

    def record_stats_once(self):
        if not self.stats_recorded:
            storage.record_run(self.score, self.coins)
            self.app.refresh_stats()
            self.stats_recorded = True

    def spawn_obstacle(self):
        bird_chance = config.BIRD_SPAWN_CHANCE + (
            (config.DIFFICULTY_MAX_BIRD_CHANCE - config.BIRD_SPAWN_CHANCE)
            * self.difficulty_t
        )
        spawn_bird = random.random() < bird_chance

        if spawn_bird:
            height_type = random.choice(["low", "high"])
            if self.last_obstacle_tag == "cactus" and height_type == "low":
                height_type = "high"
            if self.last_obstacle_tag == "bird_low" and height_type == "low":
                height_type = "high"

            self.obstacle_list.append(FlyingObstacle(height_type))
            self.last_obstacle_tag = f"bird_{height_type}"
        else:
            roll = random.random()
            if roll < 0.6:
                group_size = 1
            elif roll < 0.85:
                group_size = 2
            else:
                group_size = 3

            base_x = config.SCREEN_WIDTH + config.OBSTACLE_WIDTH
            spacing = int(config.OBSTACLE_WIDTH * 0.8 + 6)
            for i in range(group_size):
                cactus = Obstacle()
                cactus.center_x = base_x + i * spacing
                self.obstacle_list.append(cactus)

            self.last_obstacle_tag = f"cactus_{group_size}"

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.apply_day_night_background()

        if config.USE_SPRITES:
            self.particle_list.draw()
            self.coin_list.draw()
            self.powerup_list.draw()
            self.meteor_list.draw()
            self.dino_list.draw()
            self.obstacle_list.draw()
        else:
            # Manual rectangle draw to guarantee visibility when using hitbox-only mode.
            self.particle_list.draw()
            for coin in self.coin_list:
                arcade.draw_lbwh_rectangle_filled(
                    coin.left, coin.bottom, coin.width, coin.height, coin.color
                )
            for powerup in self.powerup_list:
                arcade.draw_lbwh_rectangle_filled(
                    powerup.left, powerup.bottom, powerup.width, powerup.height, powerup.color
                )
            for meteor in self.meteor_list:
                arcade.draw_lbwh_rectangle_filled(
                    meteor.left, meteor.bottom, meteor.width, meteor.height, meteor.color
                )
            for dino in self.dino_list:
                arcade.draw_lbwh_rectangle_filled(
                    dino.left, dino.bottom, dino.width, dino.height, dino.color
                )
            for obs in self.obstacle_list:
                arcade.draw_lbwh_rectangle_filled(
                    obs.left, obs.bottom, obs.width, obs.height, arcade.color.WHITE
                )
                arcade.draw_lbwh_rectangle_outline(
                    obs.left, obs.bottom, obs.width, obs.height, arcade.color.BLACK, 2
                )

        arcade.draw_text(
            f"Score: {int(self.score)}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.BLACK,
            16,
        )
        arcade.draw_text(
            f"Coins: {self.coins}",
            10,
            SCREEN_HEIGHT - 52,
            arcade.color.BLACK,
            14,
        )

        arcade.draw_text(
            f"Level: {self.level}",
            SCREEN_WIDTH - 140,
            SCREEN_HEIGHT - 90,
            arcade.color.BLACK,
            14,
        )

        if self.level_text_timer > 0:
            arcade.draw_text(
                f"LEVEL {self.level}",
                SCREEN_WIDTH // 2 - 80,
                SCREEN_HEIGHT // 2 + 80,
                arcade.color.BLACK,
                24,
            )

        if self.rule_text:
            arcade.draw_text(
                f"RULE: {self.rule_text}",
                SCREEN_WIDTH // 2 - 120,
                SCREEN_HEIGHT - 60,
                arcade.color.BLACK,
                18,
            )
        if self.active_event:
            arcade.draw_text(
                f"EVENT: {self.active_event}",
                SCREEN_WIDTH // 2 - 120,
                SCREEN_HEIGHT - 84,
                arcade.color.BLACK,
                14,
            )
        if self.golden_time_left > 0:
            arcade.draw_text(
                "GOLDEN",
                SCREEN_WIDTH // 2 - 60,
                SCREEN_HEIGHT - 108,
                arcade.color.BLACK,
                14,
            )
        if self.rule_stack > 0:
            arcade.draw_text(
                f"STACK x{self.rule_stack}",
                SCREEN_WIDTH // 2 - 90,
                SCREEN_HEIGHT - 132,
                arcade.color.BLACK,
                14,
            )

        if self.turbo_time_left > 0:
            arcade.draw_text(
                "TURBO",
                SCREEN_WIDTH - 120,
                SCREEN_HEIGHT - 30,
                arcade.color.ORANGE,
                14,
            )
        if self.shield_time_left > 0:
            arcade.draw_text(
                "SHIELD",
                SCREEN_WIDTH - 120,
                SCREEN_HEIGHT - 50,
                arcade.color.CYAN,
                14,
            )
        if self.double_jump_time_left > 0 or self.rule_double_jump:
            arcade.draw_text(
                "DOUBLE JUMP",
                SCREEN_WIDTH - 160,
                SCREEN_HEIGHT - 70,
                arcade.color.MAGENTA,
                14,
            )

        if self.paused and not self.game_over:
            arcade.draw_text(
                "PAUSED",
                SCREEN_WIDTH // 2 - 60,
                SCREEN_HEIGHT // 2 + 30,
                arcade.color.WHITE,
                24,
            )
            arcade.draw_text(
                "Press Esc to resume",
                SCREEN_WIDTH // 2 - 110,
                SCREEN_HEIGHT // 2 - 10,
                arcade.color.LIGHT_GRAY,
                14,
            )

        if DEV_MODE:
            current_rule = (
                self.rule_manager.current_rule.name
                if self.rule_manager.current_rule
                else "-"
            )
            debug_lines = [
                f"y={int(self.dino.center_y)} vy={int(self.dino.velocity_y)}",
                f"bbox w={int(self.dino.width)} h={int(self.dino.height)}",
                f"bottom={int(self.dino.bottom)} top={int(self.dino.top)}",
                f"state ground={self.dino.on_ground} crouch={self.dino.is_crouching}",
                f"jumps {self.dino.jump_count}/{self.dino.max_jumps}",
                f"gravity={int(config.GRAVITY)} jump_mult={self.jump_multiplier:.2f}",
                f"speed_mult={config.GAME_SPEED_MULTIPLIER:.2f}",
                f"diff={self.difficulty_t:.2f} t={self.difficulty_time:.1f}s",
                f"rule={current_rule} stack={self.rule_stack}",
                f"obstacles={len(self.obstacle_list)}",
                f"spawn={self.spawn_timer:.2f}/{self.next_spawn_time:.2f}",
                f"day_time={self.day_time:.1f}s",
                f"wind={self.wind_dir} t={self.wind_time_left:.1f}",
                f"powerups t={self.turbo_time_left:.1f} s={self.shield_time_left:.1f} d={self.double_jump_time_left:.1f}",
                "F1: pause rules | F2: next rule",
            ]
            for i, line in enumerate(debug_lines):
                arcade.draw_text(
                    line,
                    10,
                    10 + i * 16,
                    DEBUG_TEXT_COLOR,
                    12,
                )
            self.draw_debug_hitbox()

    def draw_debug_hitbox(self):
        arcade.draw_lrbt_rectangle_outline(
            self.dino.left,
            self.dino.right,
            self.dino.bottom,
            self.dino.top,
            arcade.color.BLACK,
            2,
        )
        for obs in self.obstacle_list:
            arcade.draw_lrbt_rectangle_outline(
                obs.left,
                obs.right,
                obs.bottom,
                obs.top,
                arcade.color.BLACK,
                2,
            )

    def spawn_run_dust(self):
        foot_offset = -12 if self.footstep_left else 12
        self.footstep_left = not self.footstep_left
        x = self.dino.center_x + foot_offset
        y = self.dino.bottom + 2
        p = make_dust_particle(x, y)
        self.particle_list.append(p)

    def spawn_land_burst(self):
        x = self.dino.center_x - 10
        y = self.dino.bottom + 6
        for _ in range(6):
            p = make_land_particle(x, y)
            self.particle_list.append(p)

    def update_player_movement(self, delta_time):
        target = self.move_dir * config.PLAYER_MOVE_SPEED
        accel_force = (
            config.PLAYER_ACCEL_SLIPPERY
            if self.slippery_active
            else config.PLAYER_ACCEL_NORMAL
        )
        friction_force = (
            config.PLAYER_FRICTION_SLIPPERY
            if self.slippery_active
            else config.PLAYER_FRICTION_NORMAL
        )
        mass = max(config.PLAYER_MASS, 0.01)
        accel = accel_force / mass
        friction = friction_force / mass

        if self.move_dir != 0:
            self.player_vel_x = self.approach(self.player_vel_x, target, accel * delta_time)
        else:
            self.player_vel_x = self.approach(self.player_vel_x, 0.0, friction * delta_time)

        self.dino.center_x += self.player_vel_x * delta_time

    @staticmethod
    def approach(current, target, delta):
        if current < target:
            return min(current + delta, target)
        if current > target:
            return max(current - delta, target)
        return current

    def spawn_coin(self):
        x = SCREEN_WIDTH + 30
        y = config.GROUND_Y + 12
        self.coin_list.append(Coin(x, y))

    def spawn_powerup(self):
        x = SCREEN_WIDTH + 30
        y = config.GROUND_Y + 14
        kind = random.choice(["turbo", "shield", "double_jump"])
        self.powerup_list.append(PowerUp(kind, x, y))

    def spawn_meteor(self):
        x = SCREEN_WIDTH + 40
        y = random.uniform(config.GROUND_Y + 80, SCREEN_HEIGHT - 140)
        self.meteor_list.append(Meteor(x, y))

    def apply_powerup(self, kind):
        if kind == "turbo":
            turbo_mult = 1.5 if storage.is_owned("turbo_plus") else 1.0
            self.turbo_time_left = config.TURBO_DURATION * turbo_mult
        elif kind == "shield":
            self.shield_time_left = config.SHIELD_DURATION
        elif kind == "double_jump":
            self.double_jump_time_left = config.DOUBLE_JUMP_DURATION

    def update_powerups(self, delta_time):
        if self.turbo_time_left > 0:
            self.turbo_time_left = max(0.0, self.turbo_time_left - delta_time)
        if self.shield_time_left > 0:
            self.shield_time_left = max(0.0, self.shield_time_left - delta_time)
        if self.double_jump_time_left > 0:
            self.double_jump_time_left = max(
                0.0, self.double_jump_time_left - delta_time
            )

        self.dino.max_jumps = (
            2 if (self.double_jump_time_left > 0 or self.rule_double_jump) else 1
        )

    def update_events(self, delta_time):
        if not self.app.enable_events:
            self.active_event = None
            self.event_time_left = 0.0
            return
        if self.event_time_left > 0:
            self.event_time_left -= delta_time
            if self.active_event == "STORM":
                self.wind_time_left = max(self.wind_time_left, 0.2)
            if self.event_time_left <= 0:
                self.active_event = None
            return

        self.event_timer += delta_time
        if self.event_timer >= self.next_event_time:
            self.event_timer = 0.0
            self.event_time_left = config.EVENT_DURATION
            self.active_event = random.choice(["FEVER", "STORM", "DOUBLE COINS"])
            if self.active_event == "STORM":
                self.wind_time_left = config.WIND_DURATION
                self.wind_dir = random.choice([-1, 1])
            self.next_event_time = random.uniform(
                config.EVENT_INTERVAL_MIN, config.EVENT_INTERVAL_MAX
            )

    def update_speed_multiplier(self):
        stack_mult = 1.0 + (self.rule_stack * config.RULE_STACK_SPEED_BONUS)
        turbo_mult = config.TURBO_SPEED_MULT if self.turbo_time_left > 0 else 1.0
        difficulty_mult = 1.0 + (
            (config.DIFFICULTY_MAX_SPEED_MULT - 1.0) * self.difficulty_t
        )
        event_mult = 1.0
        if self.active_event == "STORM":
            event_mult = 1.15
        level_mult = self.level_speed_mult
        config.GAME_SPEED_MULTIPLIER = (
            stack_mult * turbo_mult * difficulty_mult * event_mult * level_mult
        )

    def get_score_multiplier(self):
        base = 1.0 + (self.rule_stack * config.RULE_STACK_SCORE_BONUS)
        if storage.is_owned("score_boost"):
            base += 0.1
        if self.active_event == "FEVER":
            return base * config.FEVER_SCORE_MULT
        return base

    def get_spawn_interval_range(self):
        min_spawn = max(
            config.DIFFICULTY_MIN_SPAWN_INTERVAL,
            config.SPAWN_INTERVAL_MIN
            - (config.SPAWN_INTERVAL_MIN - config.DIFFICULTY_MIN_SPAWN_INTERVAL)
            * self.difficulty_t,
        )
        max_spawn = max(
            min_spawn,
            config.SPAWN_INTERVAL_MAX
            - (config.SPAWN_INTERVAL_MAX - config.DIFFICULTY_MIN_SPAWN_INTERVAL)
            * self.difficulty_t,
        )
        return min_spawn, max_spawn

    def update_wind(self, delta_time):
        if self.wind_time_left > 0:
            self.wind_time_left -= delta_time
            self.wind_particle_timer += delta_time
            if self.wind_particle_timer >= config.WIND_PARTICLE_RATE:
                self.wind_particle_timer = 0.0
                self.spawn_wind_streak()
            return

        self.wind_timer += delta_time
        if self.wind_timer >= config.WIND_INTERVAL:
            self.wind_timer = 0.0
            self.wind_time_left = config.WIND_DURATION
            self.wind_dir = random.choice([-1, 1])
            self.wind_particle_timer = 0.0

    def spawn_wind_streak(self):
        if self.wind_dir == 0:
            return
        x = -20 if self.wind_dir > 0 else SCREEN_WIDTH + 20
        y = random.uniform(config.GROUND_Y + 40, SCREEN_HEIGHT - 80)
        p = make_wind_particle(x, y, self.wind_dir)
        self.particle_list.append(p)

    def apply_day_night_background(self):
        level_idx = self.level_color_index
        day_color = config.LEVEL_DAY_COLORS[level_idx]
        night_color = config.LEVEL_NIGHT_COLORS[level_idx]
        if not self.app.enable_day_night:
            arcade.set_background_color(day_color)
            return

        t = (self.day_time % config.DAY_NIGHT_CYCLE) / config.DAY_NIGHT_CYCLE
        mix = 0.5 - 0.5 * math.cos(t * math.tau)

        def lerp(a, b, m):
            return int(a + (b - a) * m)

        r = lerp(day_color[0], night_color[0], mix)
        g = lerp(day_color[1], night_color[1], mix)
        b = lerp(day_color[2], night_color[2], mix)
        arcade.set_background_color((r, g, b))

        if mix > 0.05:
            alpha = int(config.NIGHT_OVERLAY_ALPHA * mix)
            arcade.draw_lbwh_rectangle_filled(
                0,
                0,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                (0, 0, 0, alpha),
            )
