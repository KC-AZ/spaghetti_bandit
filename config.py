PLAYER_X      = -7
CAMERA_OFFSET = 20
GROUND_Y      = -14.0
GRAPPLE_RANGE = 14

class Config:
    SCROLL_SPEED_BASE  = 4.0    # gentler start
    SCROLL_SPEED_MAX   = 18.0
    SCROLL_RAMP        = 0.035  # speed units added per second of play

    GRAVITY       = 20.0
    JUMP_FORCE    = 15.0
    LOW_JUMP_MULT = 2.0
    FALL_MULT     = 2.5

    CAR_SPAWN_BASE     = 4.5;   CAR_SPAWN_MIN     = 1.0   # fewer cars early
    DRONE_C_SPAWN_BASE = 20.0;  DRONE_C_SPAWN_MIN = 6.0   # drones rare at start
    DRONE_S_SPAWN_BASE = 18.0;  DRONE_S_SPAWN_MIN = 5.0
    HELI_SPAWN_BASE    = 5.0;   HELI_SPAWN_MIN    = 2.5   # frequent — player needs grapple points
    COIN_SPAWN_BASE    = 2.0;   COIN_SPAWN_MIN    = 0.8

    SCORE_PER_SEC = 10
    COIN_VALUE    = 50
