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
        _bbox = [Vec3(-.5,-.5,0), Vec3(.5,-.5,0), Vec3(.5,.5,0), Vec3(-.5,.5,0), Vec3(-.5,-.5,0)]
        Entity(parent=self, model=Mesh(vertices=_bbox, mode='line', thickness=2),
               color=color.orange, unlit=True, z=-0.05)
        state.drone_projectiles.append(self)

    def _remove(self):
        if self in state.drone_projectiles:
            state.drone_projectiles.remove(self)
        state._destroy(self)

    def update(self):
        if state.paused:
            return
        self.position += self.dir * self.speed * time.dt
        if (self.x < state.player.x - 6 or
                self.x > state.player.x + 50 or
                self.y < GROUND_Y - 2):
            self._remove()


# ── Charging drone ────────────────────────────────────────────────────────
class ChargingDrone(Entity):
    """
    Swoops in from the top-right, locks to the right of the player,
    tracks the player's Y while hovering, then charges at them.
    """
    def __init__(self):
        super().__init__(
            model='quad', color=color.cyan,
            scale=(1.6, 1.0),
            position=(state._spawn_x(), random.uniform(8, 14), 0),
            collider='box', name='charging_drone'
        )
        self.drone_state    = 'swooping'
        self.hover_timer    = 0.0
        self.hover_duration = random.uniform(1.5, 2.5)
        self.charge_speed   = 16.0
        self.ramp           = 0.0
        self.locked_y       = 0.0

    def update(self):
        if state.paused or not state.game_running:
            return

        min_x = camera.x + 2   # stay on the right half of the visible screen

        if self.drone_state == 'swooping':
            # Scroll left with the world but never past min_x
            self.x = max(min_x, self.x - state.scroll_speed * time.dt)
            # Swoop down toward the player's current y
            self.y += (state.player.y - self.y) * 3 * time.dt
            if self.x <= min_x + 0.5 and abs(self.y - state.player.y) < 1.5:
                self.drone_state = 'hovering'

        elif self.drone_state == 'hovering':
            # Lock x to the right of the player, keep tracking y
            self.x  = min_x
            self.y += (state.player.y - self.y) * 5 * time.dt
            self.hover_timer += time.dt
            self.color = color.red if (int(self.hover_timer * 6) % 2 == 0) else color.cyan
            if self.hover_timer >= self.hover_duration:
                self.locked_y    = self.y   # freeze y at current position
                self.drone_state = 'charging'
                self.ramp        = 0.0

        elif self.drone_state == 'charging':
            self.ramp  = min(self.ramp + time.dt * 4, 1.0)
            self.x    -= self.charge_speed * self.ramp * time.dt
            self.y     = self.locked_y      # y is frozen during the charge

        if (self.x + self.scale_x / 2 < state.player.x - 8 or
                self.x > state.player.x + 60):
            if self in state.charging_drones: state.charging_drones.remove(self)
            state._destroy(self)


# ── Shooting drone ────────────────────────────────────────────────────────
class ShootingDrone(Entity):
    """
    Drops in from the top-right, hovers and fires aimed projectiles,
    then departs. Also acts as a grapple anchor.
    """
    def __init__(self):
        target_x = camera.x + camera.fov / 2 - 2 + random.uniform(0, 3)
        target_y = random.uniform(5, 12)   # top-right area
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

        # Drift left with the world but never past a minimum right offset from the player
        self.target_pos.x = max(
            self.target_pos.x - state.scroll_speed * time.dt,
            camera.x + 2   # stay on the right half of the visible screen
        )

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
