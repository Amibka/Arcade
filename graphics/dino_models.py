from graphics.assets import load_texture_or_none, load_texture_sequence


class DinoModels:
    def __init__(self):
        self.run_textures = load_texture_sequence("assets/dino/run", max_frames=6)
        if not self.run_textures:
            # fallback 1: single file at assets/dino/run.png
            single = load_texture_or_none('assets/dino/run.png')
            if single:
                self.run_textures = [single]
            else:
                # fallback 2: single file in assets/dino/run/run.png
                single = load_texture_or_none('assets/dino/run/run.png')
                if single:
                    self.run_textures = [single]

        self.jump_texture = load_texture_or_none("assets/dino/jump.png")
        self.crouch_texture = load_texture_or_none("assets/dino/crouch.png")
