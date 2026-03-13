"""
Obstacles and grapple anchors: Car, Coin, Helicopter.
All are now placed at explicit world positions (no auto-scrolling).
"""
from ursina import *
import random, math
import state
from config import GROUND_Y


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
class Helicopter(Entity):
    def __init__(self, x, y):
        self.base_y = y
        self.bob_t  = 0.0
        super().__init__(
            model='quad', color=color.rgb(30, 110, 30),
            scale=(3.0, 1.2),
            position=(x, y, 0),
            name='helicopter'
        )
        Entity(parent=self, model='quad', color=color.rgb(60, 60, 60),
               scale=(1.3, 0.07), position=(0, 0.55, -0.01))

    def update(self):
        if state.paused or not state.game_running:
            return
        self.bob_t += time.dt * 3
        self.y      = self.base_y + math.sin(self.bob_t) * 0.15
