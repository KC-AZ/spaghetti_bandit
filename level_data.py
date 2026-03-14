"""
Hand-crafted level definitions.

Each level dict keys:
  id              int   — level number 1-5
  name            str   — display name
  length          float — world x position of the finish line
  sky_color       tuple — (r,g,b) for window background
  ground_color    tuple — (r,g,b) for ground quad (unused for now, reserved)
  cars            list  — [{'x': float}, ...]
  helicopters     list  — [{'x': float, 'y': float}, ...]
  charging_drones list  — [{'x': float, 'y': float}, ...]
  shooting_drones list  — [{'x': float, 'y': float}, ...]
  coins           list  — [{'x': float, 'y': float}, ...]
"""

LEVELS = [
    # ── Level 1 – City Streets ────────────────────────────────────────────
    # Gentle introduction: wide gaps between cars, lots of helis, no enemies.
    {
        'id': 1,
        'name': 'City Streets',
        'baseline_time': 6.53,
        'length': 200,
        'sky_color':    (135, 206, 235),
        'ground_color': ( 80, 180,  80),
        'cars': [
            {'x': 30},
            {'x': 58},
            {'x': 88},
            {'x': 118},
            {'x': 152},
            {'x': 178},
        ],
        'helicopters': [
            {'x':  42, 'y':  9},
            {'x':  74, 'y': 11},
            {'x': 104, 'y':  8},
            {'x': 136, 'y': 10},
            {'x': 166, 'y':  9},
        ],
        'charging_drones': [],
        'shooting_drones': [],
        'coins': [
            {'x':  36, 'y': -11},
            {'x':  66, 'y': -11},
            {'x':  96, 'y': -11},
            {'x': 126, 'y': -11},
            {'x': 158, 'y': -11},
        ],
    },

    # ── Level 2 – The Chase ───────────────────────────────────────────────
    # More cars, tighter gaps, two shooting drones introduced.
    {
        'id': 2,
        'name': 'The Chase',
        'baseline_time': 8.80,
        'length': 260,
        'sky_color':    (160, 200, 220),
        'ground_color': ( 90, 160,  90),
        'cars': [
            {'x': 22}, {'x': 44},
            {'x': 72}, {'x': 96},
            {'x': 124}, {'x': 148},
            {'x': 176}, {'x': 200},
            {'x': 228}, {'x': 248},
        ],
        'helicopters': [
            {'x':  52, 'y':  9},
            {'x':  88, 'y': 11},
            {'x': 132, 'y':  8},
            {'x': 168, 'y': 10},
            {'x': 212, 'y':  9},
        ],
        'charging_drones': [],
        'shooting_drones': [
            {'x':  84, 'y':  8},
            {'x': 168, 'y': 10},
        ],
        'coins': [
            {'x':  58, 'y': -11},
            {'x': 108, 'y': -11},
            {'x': 156, 'y': -11},
            {'x': 204, 'y': -11},
        ],
    },

    # ── Level 3 – Rush Hour ───────────────────────────────────────────────
    # Dense traffic, sunset sky, both drone types introduced.
    {
        'id': 3,
        'name': 'Rush Hour',
        'baseline_time': 9.50,
        'length': 310,
        'sky_color':    (255, 140,  60),
        'ground_color': ( 90, 150,  90),
        'cars': [
            {'x': 18}, {'x': 36}, {'x': 58},
            {'x': 80}, {'x': 100}, {'x': 124},
            {'x': 148}, {'x': 168}, {'x': 192},
            {'x': 216}, {'x': 240}, {'x': 262},
            {'x': 285},
        ],
        'helicopters': [
            {'x':  46, 'y': 10},
            {'x':  90, 'y':  8},
            {'x': 138, 'y': 11},
            {'x': 182, 'y':  9},
            {'x': 228, 'y': 10},
            {'x': 272, 'y':  8},
        ],
        'charging_drones': [
            {'x': 130, 'y': 12},
            {'x': 240, 'y': 11},
        ],
        'shooting_drones': [
            {'x':  72, 'y':  9},
            {'x': 195, 'y': 11},
        ],
        'coins': [
            {'x':  62, 'y': -11},
            {'x': 112, 'y': -11},
            {'x': 162, 'y': -11},
            {'x': 212, 'y': -11},
            {'x': 258, 'y': -11},
        ],
    },

    # ── Level 4 – The Gauntlet ────────────────────────────────────────────
    # Dusk sky, heavy traffic, multiple drones, tests grapple chains.
    {
        'id': 4,
        'name': 'The Gauntlet',
        'baseline_time': 9.75,
        'length': 360,
        'sky_color':    ( 70,  70, 120),
        'ground_color': ( 70, 130,  70),
        'cars': [
            {'x': 18}, {'x': 32}, {'x': 52}, {'x': 68},
            {'x': 92}, {'x': 112}, {'x': 132}, {'x': 152},
            {'x': 178}, {'x': 196}, {'x': 218}, {'x': 242},
            {'x': 264}, {'x': 284}, {'x': 308}, {'x': 328},
            {'x': 342},
        ],
        'helicopters': [
            {'x':  44, 'y': 10},
            {'x':  84, 'y':  9},
            {'x': 124, 'y': 11},
            {'x': 168, 'y':  8},
            {'x': 208, 'y': 10},
            {'x': 252, 'y':  9},
            {'x': 294, 'y': 11},
            {'x': 336, 'y':  8},
        ],
        'charging_drones': [
            {'x': 100, 'y': 12},
            {'x': 186, 'y': 11},
            {'x': 272, 'y': 12},
            {'x': 322, 'y': 10},
        ],
        'shooting_drones': [
            {'x':  62, 'y':  9},
            {'x': 144, 'y': 11},
            {'x': 234, 'y':  9},
            {'x': 302, 'y': 10},
        ],
        'coins': [
            {'x':  50, 'y': -11},
            {'x': 100, 'y': -11},
            {'x': 160, 'y': -11},
            {'x': 220, 'y': -11},
            {'x': 280, 'y': -11},
            {'x': 335, 'y': -11},
        ],
    },

    # ── Level 5 – Final Run ───────────────────────────────────────────────
    # Night sky, maximum density, the full toolkit required.
    {
        'id': 5,
        'name': 'Final Run',
        'baseline_time': 115.0,
        'length': 420,
        'sky_color':    ( 20,  15,  50),
        'ground_color': ( 50, 110,  50),
        'cars': [
            {'x': 18}, {'x': 30}, {'x': 46}, {'x': 62},
            {'x': 82}, {'x': 96}, {'x': 114}, {'x': 134},
            {'x': 154}, {'x': 170}, {'x': 190}, {'x': 210},
            {'x': 232}, {'x': 248}, {'x': 268}, {'x': 290},
            {'x': 310}, {'x': 328}, {'x': 348}, {'x': 368},
            {'x': 386}, {'x': 402},
        ],
        'helicopters': [
            {'x':  38, 'y': 10},
            {'x':  72, 'y':  9},
            {'x': 108, 'y': 11},
            {'x': 144, 'y':  8},
            {'x': 180, 'y': 10},
            {'x': 216, 'y':  9},
            {'x': 252, 'y': 11},
            {'x': 288, 'y':  8},
            {'x': 324, 'y': 10},
            {'x': 360, 'y':  9},
            {'x': 396, 'y': 11},
        ],
        'charging_drones': [
            {'x':  88, 'y': 12},
            {'x': 156, 'y': 11},
            {'x': 228, 'y': 12},
            {'x': 298, 'y': 11},
            {'x': 368, 'y': 12},
        ],
        'shooting_drones': [
            {'x':  58, 'y':  9},
            {'x': 124, 'y': 11},
            {'x': 196, 'y':  9},
            {'x': 262, 'y': 10},
            {'x': 332, 'y':  9},
            {'x': 392, 'y': 11},
        ],
        'coins': [
            {'x':  48, 'y': -11},
            {'x':  92, 'y': -11},
            {'x': 140, 'y': -11},
            {'x': 190, 'y': -11},
            {'x': 240, 'y': -11},
            {'x': 290, 'y': -11},
            {'x': 340, 'y': -11},
            {'x': 388, 'y': -11},
        ],
    },

    # ── Level 6 – Grapple Test Area ───────────────────────────────────────
    # Pure grapple practice — no enemies, no cars.
    # Section 1 (x 20–242):  uniform y=8,  every 22 units  → learn the rhythm
    # Section 2 (x 270–512): alternating y=7/11, every 22  → practice angles
    # Section 3 (x 550–784): y=9 tightly spaced, y=13 highs → speed run
    {
        'id': 6,
        'name': 'Grapple Test Area',
        'baseline_time': None,
        'length': 820,
        'sky_color':    ( 40, 180, 160),
        'ground_color': ( 60, 160, 100),
        'cars': [],
        'helicopters': [
            # Section 1 — uniform height, learn the rhythm
            {'x':  22, 'y':  8}, {'x':  55, 'y':  8}, {'x':  88, 'y':  8},
            {'x': 121, 'y':  8}, {'x': 154, 'y':  8}, {'x': 187, 'y':  8},
            {'x': 220, 'y':  8},
            # Section 2 — alternating heights, practice angles
            {'x': 270, 'y':  7}, {'x': 292, 'y': 11},
            {'x': 336, 'y':  7}, {'x': 358, 'y': 11},
            {'x': 402, 'y':  7}, {'x': 424, 'y': 11},
            {'x': 468, 'y':  7}, {'x': 490, 'y': 11},
            # Section 3 — mixed highs
            {'x': 550, 'y':  9}, {'x': 578, 'y': 13},
            {'x': 606, 'y':  9}, {'x': 634, 'y': 13},
            {'x': 662, 'y':  9}, {'x': 690, 'y': 13},
            {'x': 718, 'y':  9}, {'x': 750, 'y': 13},
            {'x': 778, 'y':  9},
        ],
        'charging_drones': [],
        'shooting_drones': [],
        'coins': [
            {'x':  33, 'y': -14}, {'x':  77, 'y': -14}, {'x': 121, 'y': -14},
            {'x': 165, 'y': -14}, {'x': 209, 'y': -14},
            {'x': 281, 'y': -14}, {'x': 325, 'y': -14}, {'x': 369, 'y': -14},
            {'x': 413, 'y': -14}, {'x': 457, 'y': -14}, {'x': 501, 'y': -14},
            {'x': 559, 'y': -14}, {'x': 595, 'y': -14}, {'x': 631, 'y': -14},
            {'x': 667, 'y': -14}, {'x': 703, 'y': -14}, {'x': 739, 'y': -14},
            {'x': 775, 'y': -14},
        ],
    },
]
