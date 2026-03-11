"""
Shared mutable state and utility functions.
Everything that multiple modules need to read or write lives here.
"""
from ursina import *
import random, math
from config import Config

# ── Entity references (assigned during main()) ────────────────────────────
audio             = None
player            = None
ground            = None
background_layers = []
game_manager      = None

# ── Entity lists ──────────────────────────────────────────────────────────
cars            = []
coins_list      = []
helicopters     = []
charging_drones   = []
shooting_drones   = []
drone_projectiles = []

# ── Game variables ────────────────────────────────────────────────────────
score        = 0.0
high_score   = 0
num_coins    = 0
elapsed      = 0.0
scroll_speed = Config.SCROLL_SPEED_BASE
paused       = False
game_running = False

# ── UI references ─────────────────────────────────────────────────────────
hud_score_text = None
hud_coins_text = None
pause_panel    = None
death_panel    = None
menu_panel     = None
settings_panel = None
rope_entity    = None


# ── Utility ───────────────────────────────────────────────────────────────
def _spawn_interval(base, minimum):
    """Difficulty ramp: linearly reduce interval from base to minimum over 120 s."""
    t = min(elapsed / 120.0, 1.0)
    return base + (minimum - base) * t

def _spawn_x():
    """X position just off the right edge of the screen."""
    return camera.x + camera.fov / 2 + random.uniform(2, 6)

def _destroy(ent):
    if ent:
        try:
            destroy(ent)
        except Exception:
            pass


# ── Rope visual ───────────────────────────────────────────────────────────
def update_rope(p1, p2):
    global rope_entity
    _destroy(rope_entity)
    rope_entity = None
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 0.01:
        return
    # Perpendicular unit vector for rope thickness (no rotation needed)
    thickness = 0.15
    px = -dy / dist * thickness
    py =  dx / dist * thickness
    # Build quad directly in world space — entity sits at origin with no rotation
    verts = [
        Vec3(p1.x - px, p1.y - py, -0.1),
        Vec3(p1.x + px, p1.y + py, -0.1),
        Vec3(p2.x + px, p2.y + py, -0.1),
        Vec3(p2.x - px, p2.y - py, -0.1),
    ]
    rope_entity = Entity(
        model=Mesh(vertices=verts, triangles=[0, 1, 2, 0, 2, 3]),
        color=color.rgb(60, 35, 10),   # dark brown — visible against sky and ground
        double_sided=True,
        unlit=True,
    )

def clear_rope():
    global rope_entity
    _destroy(rope_entity)
    rope_entity = None
