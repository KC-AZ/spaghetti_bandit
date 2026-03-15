"""
Obstacles and grapple anchors: Car, Coin, Helicopter.
All are placed at explicit world positions (no auto-scrolling).
"""
import math
import random
from ursina import *
import state
from config import GROUND_Y, GRAPPLE_RANGE


# ── Car ────────────────────────────────────────────────────────────────────
CAR_DEFS = [
    (1.8, 0.9,  color.rgb32(140, 140, 220)),  # small
    (2.8, 1.2,  color.rgb32(100, 190, 100)),  # medium
    (3.8, 1.5,  color.rgb32(210, 150,  70)),  # large
    (5.2, 2.3,  color.rgb32(210,  70,  70)),  # truck
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


# ── Helicopter timing circle helpers ───────────────────────────────────────
_HELI_INNER_R   = 0.2    # world-space radius of the inner static dot
_HELI_OUTER_MAX = 3.5    # world-space radius of the outer ring when player is far
_HELI_DETECT    = 50.0   # distance at which outer ring is at its maximum size


def _disc_mesh(segments=24):
    verts = [Vec3(0, 0, 0)]
    for i in range(segments):
        a = math.tau * i / segments
        verts.append(Vec3(math.cos(a) * 0.5, math.sin(a) * 0.5, 0))
    tris = []
    for i in range(segments):
        tris += [0, i + 1, (i + 1) % segments + 1]
    return Mesh(vertices=verts, triangles=tris)


def _ring_mesh(segments=36):
    verts = [Vec3(math.cos(math.tau * i / segments) * 0.5,
                  math.sin(math.tau * i / segments) * 0.5, 0)
             for i in range(segments + 1)]
    return Mesh(vertices=verts, mode='line', thickness=2)


# ── Helicopter ─────────────────────────────────────────────────────────────
class Helicopter(Entity):
    _SW = 3.0   # body scale x
    _SH = 1.2   # body scale y

    def __init__(self, x, y):
        self.base_y = y
        self.bob_t  = 0.0
        super().__init__(
            model='quad', color=color.rgb32(90, 55, 25),   # dark brown
            scale=(self._SW, self._SH),
            position=(x, y, 0),
            name='helicopter',
            unlit=True,
        )
        # Rotor blade
        Entity(parent=self, model='quad', color=color.rgb32(60, 60, 60),
               scale=(1.3, 0.07), position=(0, 0.55, -0.01))

        # Inner static dot — small square marker, sits in front of the body
        ir = _HELI_INNER_R
        self._inner = Entity(
            parent=self,
            model=_disc_mesh(),
            color=color.white,
            scale=(2 * ir / self._SW, 2 * ir / self._SH, 1),
            position=(0, 0, -0.05),
            unlit=True,
        )

        # Outer reactive ring — in front of body so it's always visible
        self._outer = Entity(
            parent=self,
            model=_ring_mesh(),
            color=color.white,
            scale=(2 * _HELI_OUTER_MAX / self._SW,
                   2 * _HELI_OUTER_MAX / self._SH, 1),
            position=(0, 0, -0.1),
            unlit=True,
        )

    def update(self):
        if state.paused or not state.game_running:
            return
        self.bob_t += time.dt * 3
        self.y      = self.base_y + math.sin(self.bob_t) * 0.15

        # Shrink outer ring as player closes in on grapple range
        dist = math.sqrt((state.player.x - self.x) ** 2 +
                         (state.player.y - self.y) ** 2)
        t = max(0.0, min(1.0,
                (dist - GRAPPLE_RANGE) / (_HELI_DETECT - GRAPPLE_RANGE)))
        r = _HELI_INNER_R + t * (_HELI_OUTER_MAX - _HELI_INNER_R)
        self._outer.scale = (2 * r / self._SW, 2 * r / self._SH, 1)


# ── Launch Point ────────────────────────────────────────────────────────────
class LaunchPoint(Entity):
    _SW = 2.0   # body scale x
    _SH = 0.5   # body scale y — flat pad shape

    def __init__(self, x, y):
        self.base_y = y
        self.bob_t  = 0.0
        super().__init__(
            model='quad', color=color.rgb32(220, 120, 20),   # orange
            scale=(self._SW, self._SH),
            position=(x, y, 0),
            name='launch_point',
            unlit=True,
        )
        # Chevron arrow pointing right — suggests launch direction
        Entity(parent=self, model='quad', color=color.rgb32(255, 220, 50),
               scale=(0.5, 0.5), position=(0, 0, -0.01), rotation_z=45)

        # Inner static dot
        ir = _HELI_INNER_R
        self._inner = Entity(
            parent=self,
            model=_disc_mesh(),
            color=color.white,
            scale=(2 * ir / self._SW, 2 * ir / self._SH, 1),
            position=(0, 0, -0.05),
            unlit=True,
        )

        # Outer reactive ring
        self._outer = Entity(
            parent=self,
            model=_ring_mesh(),
            color=color.rgb32(255, 180, 50),   # orange-yellow ring
            scale=(2 * _HELI_OUTER_MAX / self._SW,
                   2 * _HELI_OUTER_MAX / self._SH, 1),
            position=(0, 0, -0.1),
            unlit=True,
        )

    def update(self):
        if state.paused or not state.game_running:
            return
        self.bob_t += time.dt * 2
        self.y      = self.base_y + math.sin(self.bob_t) * 0.1

        # Shrink outer ring as player closes in on grapple range
        dist = math.sqrt((state.player.x - self.x) ** 2 +
                         (state.player.y - self.y) ** 2)
        t = max(0.0, min(1.0,
                (dist - GRAPPLE_RANGE) / (_HELI_DETECT - GRAPPLE_RANGE)))
        r = _HELI_INNER_R + t * (_HELI_OUTER_MAX - _HELI_INNER_R)
        self._outer.scale = (2 * r / self._SW, 2 * r / self._SH, 1)
