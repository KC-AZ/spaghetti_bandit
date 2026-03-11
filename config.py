PLAYER_X      = -7
CAMERA_OFFSET = 20
GROUND_Y      = -14.0
GRAPPLE_RANGE = 30

class Config:
    SCROLL_SPEED_BASE  = 7.0    # gentler start
    SCROLL_SPEED_MAX   = 18.0
    SCROLL_RAMP        = 0.035  # speed units added per second of play

    GRAVITY           = 38.0
    JUMP_FORCE        = 17.0
    DOUBLE_JUMP_FORCE = 13.0   # second jump is weaker — recovery, not full leap
    FALL_MULT         = 3.5
    COYOTE_TIME       = 0.1    # seconds after leaving ground where jump still works

    CAR_SPAWN_BASE     = 4.5;   CAR_SPAWN_MIN     = 1.0   # fewer cars early
    DRONE_C_SPAWN_BASE = 20.0;  DRONE_C_SPAWN_MIN = 6.0   # drones rare at start
    DRONE_S_SPAWN_BASE = 18.0;  DRONE_S_SPAWN_MIN = 5.0
    HELI_SPAWN_BASE    = 5.0;   HELI_SPAWN_MIN    = 2.5   # frequent — player needs grapple points
    COIN_SPAWN_BASE    = 2.0;   COIN_SPAWN_MIN    = 0.8

    SCORE_PER_SEC = 10
    COIN_VALUE    = 50

    GRAPPLE_SPRING_K   = 4.0   # spring pulling player back to PLAYER_X after swing
    GRAPPLE_X_DRAG     = 0.08  # air drag — momentum persists while airborne
    GROUND_FRICTION    = 5.0   # ground drag — bleeds speed fast if you don't bhop

    BHOP_BOOST         = 3.0   # forward vel_x added per successful bhop
    BHOP_MAX_VEL_X     = 20.0  # high cap — speed is earned through skill
    BHOP_BUFFER        = 0.25  # generous window so timing is easy
    GRAPPLE_MIN_ROPE   = 6.0   # minimum rope length after reel-in
    GRAPPLE_REEL_SPEED = 12.0  # units per second to pull player toward anchor
    GRAPPLE_SWING_MULT = 2.5   # gravity multiplier inside the pendulum (snappier swing)
