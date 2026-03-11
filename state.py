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
charging_drones = []
shooting_drones = []

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
    dx, dy = p2.x - p1.x, p2.y - p1.y
    dist   = math.sqrt(dx * dx + dy * dy)
    if dist < 0.01:
        return
    if rope_entity is None:
        rope_entity = Entity(model='quad', color=color.white, z=-0.1)
    rope_entity.position   = Vec3((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, -0.1)
    rope_entity.scale      = Vec3(dist, 0.07, 1)
    rope_entity.rotation_z = math.degrees(math.atan2(dy, dx))

def clear_rope():
    global rope_entity
    _destroy(rope_entity)
    rope_entity = None
