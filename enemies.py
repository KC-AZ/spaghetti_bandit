"""
Enemies: ChargingDrone, ShootingDrone, DroneProjectile.
"""
from ursina import *
import random
import state
from config import GROUND_Y


# ── Drone projectile ──────────────────────────────────────────────────────
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

    def update(self):
        if state.paused:
            return
        self.position += self.dir * self.speed * time.dt
        if (self.x < state.player.x - 6 or
                self.x > state.player.x + 50 or
                self.y < GROUND_Y - 2):
            state._destroy(self)


# ── Charging drone ────────────────────────────────────────────────────────
class ChargingDrone(Entity):
    """
    Drifts in from the right, hovers and flashes red to telegraph,
    then locks onto the player's Y and charges across the screen.
    """
    def __init__(self):
        hover_y = random.uniform(GROUND_Y + 2, GROUND_Y + 10)
        super().__init__(
            model='quad', color=color.cyan,
            scale=(1.6, 1.0),
            position=(state._spawn_x(), hover_y, 0),
            collider='box', name='charging_drone'
        )
        self.drone_state    = 'approaching'
        self.hover_y        = hover_y
        self.hover_timer    = 0.0
        self.hover_duration = random.uniform(1.8, 3.0)
        self.charge_speed   = 14.0
        self.locked_y       = None
        self.ramp           = 0.0   # smooth charge ramp-up

    def update(self):
        if state.paused or not state.game_running:
            return

        if self.drone_state == 'approaching':
            self.x -= state.scroll_speed * time.dt
            diff_y  = self.hover_y - self.y
            self.y += diff_y * 5 * time.dt
            if abs(diff_y) < 0.2:
                self.drone_state = 'hovering'

        elif self.drone_state == 'hovering':
            self.x           -= state.scroll_speed * time.dt
            self.hover_timer  += time.dt
            self.color = color.red if (int(self.hover_timer * 6) % 2 == 0) else color.cyan
            if self.hover_timer >= self.hover_duration:
                self.locked_y    = state.player.y
                self.drone_state = 'charging'
                self.ramp        = 0.0

        elif self.drone_state == 'charging':
            self.ramp  = min(self.ramp + time.dt * 4, 1.0)
            self.x    -= self.charge_speed * self.ramp * time.dt
            self.y    += (self.locked_y - self.y) * 0.12

        if (self.x + self.scale_x / 2 < state.player.x - 8 or
                self.x > state.player.x + 50 or
                self.y < GROUND_Y - 1):
            if self in state.charging_drones: state.charging_drones.remove(self)
            state._destroy(self)


# ── Shooting drone ────────────────────────────────────────────────────────
class ShootingDrone(Entity):
    """
    Drops in from the top-right, hovers and fires aimed projectiles,
    then departs. Also acts as a grapple anchor.
    """
    def __init__(self):
        target_x = camera.x + camera.fov / 2 - 3 + random.uniform(-1.5, 1.5)
        target_y = GROUND_Y + random.uniform(8, 13) + random.uniform(-1.0, 1.0)
        super().__init__(
            model='quad', color=color.magenta,
            scale=(1.6, 1.0),
            position=(target_x, target_y + 8, 0),   # spawn above target
            collider='box', name='shooting_drone'
        )
        self.target_pos     = Vec3(target_x, target_y, 0)
        self.drone_state    = 'approaching'
        self.approach_timer = 0.0
        self.hover_timer    = 0.0
        self.hover_duration = random.uniform(4.0, 6.5)
        self.shoot_timer    = 0.0
        self.shoot_interval = random.uniform(1.0, 2.0)
        self.depart_speed   = 6.0

    def update(self):
        if state.paused or not state.game_running:
            return

        # Keep target drifting left so the drone stays in a consistent screen position
        self.target_pos.x -= state.scroll_speed * time.dt

        if self.drone_state == 'approaching':
            self.position       = lerp(self.position, self.target_pos, 3 * time.dt)
            self.approach_timer += time.dt
            if self.approach_timer >= 1.2:
                self.drone_state = 'hovering'

        elif self.drone_state == 'hovering':
            self.position    = lerp(self.position, self.target_pos, 6 * time.dt)
            self.hover_timer += time.dt
            self.shoot_timer += time.dt
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0.0
                DroneProjectile(start_pos=Vec3(self.x, self.y, 0),
                                direction=state.player.position - self.position)
            if self.hover_timer >= self.hover_duration:
                self.drone_state = 'departing'

        elif self.drone_state == 'departing':
            self.x += self.depart_speed * time.dt
            self.y += self.depart_speed * 0.5 * time.dt
            if (self.x > state.player.x + 50 or
                    self.y > 20):
                if self in state.shooting_drones: state.shooting_drones.remove(self)
                state._destroy(self)
