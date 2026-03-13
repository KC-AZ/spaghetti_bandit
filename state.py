"""
Shared mutable state and utility functions.
"""
import math
import json
import os
import sys as _sys
from ursina import *
from config import Config

# ── Entity references ──────────────────────────────────────────────────────
audio             = None
player            = None
ground            = None
background_layers = []
game_manager      = None
finish_line       = None

# ── Entity lists ───────────────────────────────────────────────────────────
cars              = []
coins_list        = []
helicopters       = []
charging_drones   = []
shooting_drones   = []
drone_projectiles = []

# ── Game / level state ─────────────────────────────────────────────────────
current_level  = 1
level_timer    = 0.0
level_complete = False
num_coins      = 0
paused         = False
game_running   = False

# ── Personal bests ─────────────────────────────────────────────────────────
# { level_id (int): best_time (float) }
pbs = {}

# Save location: next to the executable when frozen, next to this file otherwise.
_BASE = (os.path.dirname(_sys.executable)
         if getattr(_sys, 'frozen', False)
         else os.path.dirname(os.path.abspath(__file__)))
PB_FILE = os.path.join(_BASE, 'saves', 'pbs.json')


def load_pbs():
    global pbs
    if os.path.exists(PB_FILE):
        try:
            with open(PB_FILE) as f:
                raw = json.load(f)
            pbs = {int(k): float(v) for k, v in raw.items()}
        except Exception:
            pbs = {}


def save_pbs():
    os.makedirs(os.path.dirname(PB_FILE), exist_ok=True)
    with open(PB_FILE, 'w') as f:
        json.dump(pbs, f)


# ── UI references ──────────────────────────────────────────────────────────
hud_bg               = None
hud_timer_text       = None
hud_level_text       = None
hud_coins_text       = None
hud_goal_text        = None
hud_parry_text       = None
pause_panel          = None
death_panel          = None
menu_panel           = None
settings_panel       = None
level_select_panel   = None
level_complete_panel = None
rope_entity          = None


# ── Utility ────────────────────────────────────────────────────────────────
def _destroy(ent):
    if ent:
        try:
            destroy(ent)
        except Exception:
            pass


# ── Rope visual ────────────────────────────────────────────────────────────
def update_rope(p1, p2):
    global rope_entity
    _destroy(rope_entity)
    rope_entity = None
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 0.01:
        return
    thickness = 0.15
    px = -dy / dist * thickness
    py =  dx / dist * thickness
    verts = [
        Vec3(p1.x - px, p1.y - py, -0.1),
        Vec3(p1.x + px, p1.y + py, -0.1),
        Vec3(p2.x + px, p2.y + py, -0.1),
        Vec3(p2.x - px, p2.y - py, -0.1),
    ]
    rope_entity = Entity(
        model=Mesh(vertices=verts, triangles=[0, 1, 2, 0, 2, 3]),
        color=color.rgb(60, 35, 10),
        double_sided=True,
        unlit=True,
    )


def clear_rope():
    global rope_entity
    _destroy(rope_entity)
    rope_entity = None
