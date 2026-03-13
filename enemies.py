"""
Enemies: ChargingDrone, ShootingDrone, DroneProjectile.
Enemies are placed at world positions and activate when the player approaches.
"""
import math
import random
from ursina import *
import state
from config import GROUND_Y


# ── Drone projectile ───────────────────────────────────────────────────────
class DroneProjectile(Entity):
    def __init__(self, start_pos, direction):
        self.dir   = direction.normalized()
        self.speed = 11
        super().__init__(
            model='quad', color=color.yellow,
            scale=(0.45, 0.45),
            position=start_pos,
            collider='box', name='drone_projectile'
        )
        _bbox = [Vec3(-.5, -.5, 0), Vec3(.5, -.5, 0), Vec3(.5, .5, 0), Vec3(-.5, .5, 0), Vec3(-.5, -.5, 0)]
        Entity(parent=self, model=Mesh(vertices=_bbox, mode='line', thickness=2),
               color=color.orange, unlit=True, z=-0.05)
        state.drone_projectiles.append(self)

    def _remove(self):
        if self in state.drone_projectiles:
            state.drone_projectiles.remove(self)
        state._destroy(self)

    def update(self):
        if state.paused or not state.game_running:
            return
        self.position += self.dir * self.speed * time.dt
        # Despawn when well off-screen relative to the player
        if (self.x < state.player.x - 8 or
                self.x > state.player.x + 60 or
                self.y < GROUND_Y - 2):
            self._remove()


# ── Charging drone ─────────────────────────────────────────────────────────
class ChargingDrone(Entity):
    """
    Waits at its world position until the player is close, then repositions
    just off-screen right and swoops in at a fixed speed.
    """
    HOVER_CAM_OFFSET = 18   # units right of camera centre while hovering (near far-right edge)
    SWOOP_SPEED      = 35   # units/s — outruns any player bhop speed
    ACTIVATION_DIST  = 30

    def __init__(self, x, y):
        super().__init__(
            model='quad', color=color.cyan,
            scale=(1.6, 1.0),
            position=(x, y, 0),
            collider='box', name='charging_drone'
        )
        self.trigger_x      = x
        self.spawn_y        = y
        self.drone_state    = 'waiting'
        self.hover_timer    = 0.0
        self.swoop_timer    = 0.0
        self.hover_duration = random.uniform(1.5, 2.5)
        self.charge_speed   = 22.0
        self.ramp           = 0.0
        self.locked_y       = 0.0

    def update(self):
        if state.paused or not state.game_running:
            return

        if self.drone_state == 'waiting':
            if state.player.x > self.trigger_x - self.ACTIVATION_DIST:
                # Start well off the right edge so the swoop-in is fully visible
                self.x = camera.x + 42
                self.y = self.spawn_y
                self.drone_state = 'swooping'
            return

        hover_x = camera.x + self.HOVER_CAM_OFFSET   # far-right anchor, updates every frame

        if self.drone_state == 'swooping':
            target_x = hover_x
            target_y = state.player.y
            dx = target_x - self.x
            dy = target_y - self.y
            d  = max(0.1, math.sqrt(dx * dx + dy * dy))
            self.x += (dx / d) * self.SWOOP_SPEED * time.dt
            self.y += (dy / d) * self.SWOOP_SPEED * time.dt
            self.swoop_timer += time.dt
            if abs(self.x - target_x) < 2.0 or self.swoop_timer > 4.0:
                self.drone_state = 'hovering'
                self.hover_timer = 0.0

        elif self.drone_state == 'hovering':
            # Lock to far-right edge of screen; smooth y to match player height
            self.x  = hover_x
            self.y += (state.player.y - self.y) * 6 * time.dt
            self.hover_timer += time.dt
            self.color = color.red if (int(self.hover_timer * 6) % 2 == 0) else color.cyan
            if self.hover_timer >= self.hover_duration:
                self.locked_y    = self.y
                self.drone_state = 'charging'
                self.ramp        = 0.0

        elif self.drone_state == 'charging':
            self.ramp  = min(self.ramp + time.dt * 4, 1.0)
            self.x    -= self.charge_speed * self.ramp * time.dt
            self.y     = self.locked_y

        # Despawn when well behind the player
        if self.x + self.scale_x / 2 < state.player.x - 15:
            if self in state.charging_drones:
                state.charging_drones.remove(self)
            state._destroy(self)


# ── Ground shooter ─────────────────────────────────────────────────────────
class ShootingDrone(Entity):
    """
    Static ground enemy. Stands on the floor and fires at the player
    when they get within range. Kept as ShootingDrone for level-data compat.
    """
    SCALE_W         = 0.9
    SCALE_H         = 1.6
    ACTIVATION_DIST = 35

    def __init__(self, x, y):   # y from level data is ignored — always on ground
        ground_y = GROUND_Y + 0.5 + self.SCALE_H / 2
        super().__init__(
            model='quad', color=color.rgb32(200, 55, 55),
            scale=(self.SCALE_W, self.SCALE_H),
            position=(x, ground_y, 0),
            collider='box', name='shooting_drone'
        )
        self.trigger_x      = x
        self.active         = False
        self.shoot_timer    = 0.0
        self.shoot_interval = random.uniform(1.5, 2.5)

    def update(self):
        if state.paused or not state.game_running:
            return

        if not self.active:
            if state.player.x > self.trigger_x - self.ACTIVATION_DIST:
                self.active = True
            return

        self.shoot_timer += time.dt
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0.0
            # Fire from upper body toward player
            origin = Vec3(self.x, self.y + self.scale_y * 0.25, 0)
            DroneProjectile(start_pos=origin,
                            direction=state.player.position - origin)

        # Despawn once well behind the player
        if self.x < state.player.x - 20:
            if self in state.shooting_drones:
                state.shooting_drones.remove(self)
            state._destroy(self)
