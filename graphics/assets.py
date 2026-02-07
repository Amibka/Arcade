import os
import sys
import arcade
import config


def has_valid_asset(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 0


def resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def load_sprite_or_solid(path: str, width: int, height: int, color):
    resolved = resource_path(path)
    if config.USE_SPRITES and has_valid_asset(resolved):
        sprite = arcade.Sprite(resolved)
        sprite.width = width
        sprite.height = height
        return sprite
    return arcade.SpriteSolidColor(width, height, color)


def load_texture_or_none(path: str):
    resolved = resource_path(path)
    if config.USE_SPRITES and has_valid_asset(resolved):
        return arcade.load_texture(resolved)
    return None


def load_texture_sequence(prefix: str, max_frames: int = 8):
    textures = []
    for i in range(max_frames):
        path = f"{prefix}_{i}.png"
        tex = load_texture_or_none(path)
        if tex:
            textures.append(tex)
    return textures
