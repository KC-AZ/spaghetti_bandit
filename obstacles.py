"""
Obstacles and grapple anchors: Car, Coin, Helicopter.
All are now placed at explicit world positions (no auto-scrolling).
"""
from ursina import *
import random, math
import state
from config import GROUND_Y, GRAPPLE_RANGE


# ── Car ────────────────────────────────────────────────────────────────────
CAR_DEFS = [
    (1.8, 0.9,  color.rgb(140, 140, 220)),  # small
    (2.8, 1.2,  color.rgb(100, 190, 100)),  # medium
    (3.8, 1.5,  color.rgb(210, 150,  70)),  # large
    (5.2, 2.3,  color.rgb(210,  70,  70)),  # truck
]

class Car(Entity):
    def __init__(self, x):
        w, h, col = random.choice(CAR_DEFS)
        super().__init__(
            model='quad', color=col,
            scale=(w, h),
            position=(x, GROUND_Y + 0.5 + h / 2, 0),
            collider='box', name='car'
        )
        # Wheels in normalised local space
        for wx in (-0.28, 0.28):
            Entity(parent=self, model='quad', color=color.dark_gray,
                   scale=(0.14, 0.2), position=(wx, -0.42, -0.01))


# ── Coin ───────────────────────────────────────────────────────────────────
class Coin(Entity):
    def __init__(self, x, y):
        self.base_y = y
        self.bob_t  = random.uniform(0, math.tau)
        super().__init__(
            model='quad', color=color.yellow,
            scale=(0.65, 0.65),
            position=(x, y, 0),
            collider='box', name='coin'
        )

    def update(self):
        if state.paused or not state.game_running:
            return
        self.bob_t += time.dt * 3
        self.y      = self.base_y + math.sin(self.bob_t) * 0.25


# ── Helicopter ─────────────────────────────────────────────────────────────
def _make_ring_mesh(segments=48):
    verts = [Vec3(math.cos(math.tau * i / segments) * 0.5,
                  math.sin(math.tau * i / segments) * 0.5, 0)
             for i in range(segments + 1)]
    return Mesh(vertices=verts, mode='line', thickness=2)


class Helicopter(Entity):
    _SW = 3.0   # entity scale_x
    _SH = 1.2   # entity scale_y

    def __init__(self, x, y):
        self.base_y  = y
        self.bob_t   = 0.0
        self.pulse_t = 0.0
        super().__init__(
            model='quad', color=color.rgb(30, 110, 30),
            scale=(self._SW, self._SH),
            position=(x, y, 0),
            name='helicopter'
        )
        # Rotor blade
        Entity(parent=self, model='quad', color=color.rgb(60, 60, 60),
               scale=(1.3, 0.07), position=(0, 0.55, -0.01))

        # Range ring — pulses green when player is within grapple range.
        _R = 3.0
        self._ring = Entity(
            parent=self, unlit=True,
            model=_make_ring_mesh(),
            scale=(2 * _R / self._SW, 2 * _R / self._SH),
            color=color.rgba(80, 255, 80, 0),
            z=-0.03
        )

    def update(self):
        if state.paused or not state.game_running:
            return
        self.bob_t += time.dt * 3
        self.y      = self.base_y + math.sin(self.bob_t) * 0.15

        p = state.player
        if p and p.alive and distance(self.position, p.position) <= GRAPPLE_RANGE:
            self.pulse_t += time.dt * 6
            alpha = int(140 + 80 * math.sin(self.pulse_t))
            self._ring.color = color.rgba(80, 255, 80, alpha)
        else:
            self.pulse_t = 0.0
            self._ring.color = color.rgba(80, 255, 80, 0)
