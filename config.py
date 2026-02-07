# ======================
# WINDOW
# ======================
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Dino Runner - Change Rules"

# ======================
# MODE
# ======================
DEV_MODE = False
USE_SPRITES = False
# ======================
# DEV HOTKEYS
# ======================
DEV_FREEZE_RULES = False

# ======================
# DEBUG
# ======================
DEBUG_TEXT_COLOR = (90, 90, 90)
SHOW_DEBUG_INFO = True

# ======================
# DAY / NIGHT
# ======================
DAY_NIGHT_CYCLE = 120.0  # seconds for a full cycle (day->night->day)
DAY_COLOR = (220, 220, 220)
NIGHT_COLOR = (80, 80, 80)
NIGHT_OVERLAY_ALPHA = 70
LEVEL_DAY_COLORS = [
    (255, 255, 255),
    (242, 250, 255),
    (250, 244, 232),
    (240, 246, 238),
    (245, 238, 250),
]
LEVEL_NIGHT_COLORS = [
    (180, 190, 210),
    (160, 175, 200),
    (190, 180, 160),
    (170, 190, 175),
    (175, 165, 190),
]

# ======================
# GAMEPLAY
# ======================
GROUND_Y = 80

# ======================
# DINO
# ======================
DINO_STAND_WIDTH = 44
DINO_STAND_HEIGHT = 70
DINO_JUMP_VELOCITY = 900
DINO_CROUCH_HEIGHT = 24
DINO_CROUCH_WIDTH = 52
JUMP_BUFFER_TIME = 0.1
COYOTE_TIME = 0.08
JUMP_TIME_TO_APEX = 0.32
JUMP_CUTOFF_MULT = 0.5
PLAYER_MOVE_SPEED = 260
PLAYER_ACCEL_NORMAL = 1200
PLAYER_ACCEL_SLIPPERY = 400
PLAYER_FRICTION_NORMAL = 1600
PLAYER_FRICTION_SLIPPERY = 300
PLAYER_MASS = 1.0

# ======================
# PHYSICS
# ======================
GRAVITY = 2000
TERMINAL_VELOCITY = 1800
AIR_DRAG = 0.6  # higher = more air resistance

# ======================
# OBSTACLES
# ======================
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 60
OBSTACLE_SPEED = 300
SPAWN_INTERVAL = 2.0
SPAWN_INTERVAL_MIN = 1.4
SPAWN_INTERVAL_MAX = 2.6
BIRD_SPAWN_CHANCE = 0.35
GAME_SPEED_MULTIPLIER = 1.0

# ======================
# DIFFICULTY SCALING
# ======================
DIFFICULTY_RAMP_DURATION = 180.0  # seconds to reach max difficulty
DIFFICULTY_MAX_SPEED_MULT = 1.35
DIFFICULTY_MIN_SPAWN_INTERVAL = 1.2
DIFFICULTY_MAX_BIRD_CHANCE = 0.5
# ======================
# LEVELS
# ======================
LEVEL_SCORE_STEP = 150
LEVEL_MAX = 5
LEVEL_SPEED_STEP = 0.06

# ======================
# WIND
# ======================
WIND_INTERVAL = 8.0
WIND_DURATION = 2.5
WIND_FORCE = 180
WIND_PARTICLE_RATE = 0.08

# ======================
# POWERUPS / COINS
# ======================
COIN_SPAWN_INTERVAL = 3.0
COIN_SPAWN_CHANCE = 0.6
POWERUP_SPAWN_INTERVAL = 6.0
POWERUP_SPAWN_CHANCE = 0.5
TURBO_DURATION = 5.0
TURBO_SPEED_MULT = 1.35
SHIELD_DURATION = 8.0
DOUBLE_JUMP_DURATION = 8.0

# ======================
# EVENTS
# ======================
EVENT_INTERVAL_MIN = 18.0
EVENT_INTERVAL_MAX = 30.0
EVENT_DURATION = 6.0
FEVER_SCORE_MULT = 2.0
FEVER_COIN_BONUS = 0.25
STORM_WIND_FORCE_MULT = 1.4
DOUBLE_COIN_MULT = 2

# ======================
# EASTER EGGS
# ======================
GOLDEN_STREAK_COINS = 100
GOLDEN_DURATION = 30.0
METEOR_SPAWN_CHANCE = 0.01
METEOR_SCORE_BONUS = 50

# ======================
# RULE STACKS
# ======================
RULE_STACK_MAX = 3
RULE_STACK_SPEED_BONUS = 0.08
RULE_STACK_SCORE_BONUS = 0.1

# ======================
# RULE SYSTEM (ПОТОМ)
# ======================
RULE_CHANGE_INTERVAL = 10.0
RULE_COMBO_CHANCE = 0.35

# ======================
# PHYSICS PRESETS (RULES)
# ======================
GRAVITY_LOW = 1200
GRAVITY_NORMAL = 2000
GRAVITY_HIGH = 2200

# ======================
# OBSTACLE SPEED PRESETS
# ======================
OBSTACLE_SPEED_SLOW = 200
OBSTACLE_SPEED_NORMAL = 300
OBSTACLE_SPEED_FAST = 450

# ======================
# JUMP LIMITS
# ======================
MAX_JUMP_HEIGHT = 260  # px от земли
# ======================
# JUMP HEIGHTS
# ======================
MAX_JUMP_HEIGHT_NORMAL = 260
MAX_JUMP_HEIGHT_HIGH = 56
MAX_JUMP_HEIGHT_LOW = 300

# ======================
# FLYING OBSTACLES
# ======================
BIRD_HEIGHT_LOW = 140     # надо прыгать
BIRD_HEIGHT_HIGH = 220    # можно пробежать

# минимальная дистанция между сложными препятствиями
SAFE_SPAWN_GAP = 1.2  # секунды



