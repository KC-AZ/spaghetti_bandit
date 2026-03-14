CAMERA_OFFSET = 20
GROUND_Y      = -18.0
GRAPPLE_RANGE = 30


class Config:
    # Movement
    WALK_SPEED  = 8.0    # units/s walking left or right
    DUCK_SPEED  = 4.0    # units/s while ducking

    # Jump / gravity
    GRAVITY           = 38.0
    JUMP_FORCE        = 17.0
    DOUBLE_JUMP_FORCE = 13.0   # second jump is weaker — recovery tool
    FALL_MULT         = 3.5    # gravity multiplier on the way down
    COYOTE_TIME       = 0.1    # seconds after leaving ground where jump still works

    # Bhop
    BHOP_BOOST     = 3.0    # vel_x added per bhop (diminishing returns apply)
    BHOP_MAX_VEL_X = 20.0   # hard cap — earned through grapple chains
    BHOP_BUFFER    = 0.25   # input buffer window (easy timing)

    # Horizontal drag
    GRAPPLE_X_DRAG  = 0.08  # air drag — momentum persists while airborne
    GROUND_FRICTION = 2.5   # ground drag — speed bleeds if you don't bhop

    # Grapple
    GRAPPLE_MIN_ROPE        = 6.0
    GRAPPLE_REEL_SPEED      = 17.5   # how fast the rope pulls in
    GRAPPLE_SWING_MULT      = 2.5
    GRAPPLE_REEL_MIN_LENGTH = 8.0    # below this rope length, no reel-in
    GRAPPLE_SLACK_MAX       = 16.0   # max rope length for slack phase; beyond this snaps taut immediately

    # Collectibles
    COIN_VALUE = 50
