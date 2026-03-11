"""
Player entity: movement, jump, grapple swing, animation, collision.
"""
from ursina import *
import math
import state
from config import Config, PLAYER_X, GROUND_Y, GRAPPLE_RANGE


class Player(Entity):
    def __init__(self):
        super().__init__(
            model='quad',
            texture=load_texture('idle.png'),
            scale=(3, 3),
            position=(PLAYER_X, GROUND_Y + 1.5),
            collider='box',
            name='player',
            z=0
        )
        self.textures = {
            'idle':    load_texture('idle.png'),
            'running': load_texture('run.png'),
            'jumping': load_texture('jump.png'),
        }
        self.frame_counts = {'idle': 10, 'running': 8, 'jumping': 6}
        self.frame_frac   = 0.9

        self.anim_state    = 'idle'
        self.current_frame = 0
        self.anim_timer    = 0.0
        self.anim_speed    = 0.09
        self._apply_frame()

        self.vel_y     = 0.0
        self.on_ground = False
        self.alive     = True

        # Grapple state
        self.grappling      = False
        self.grapple_anchor = None
        self.rope_length    = 0.0
        self.swing_angle    = 0.0   # radians from anchor (0 = right)
        self.angular_vel    = 0.0

    # ── Animation ─────────────────────────────────────────────────────────
    def _apply_frame(self):
        n       = self.frame_counts[self.anim_state]
        seg     = 1.0 / n
        padding = seg * (1 - self.frame_frac) / 2
        self.texture_scale  = (seg * self.frame_frac, 1)
        self.texture_offset = (self.current_frame * seg + padding, 0)

    def _set_anim(self, anim):
        if anim == self.anim_state:
            return
        self.anim_state    = anim
        self.current_frame = 0
        self.anim_timer    = 0.0
        self.texture       = self.textures[anim]
        self._apply_frame()

    # ── Jump ──────────────────────────────────────────────────────────────
    def do_jump(self):
        if self.on_ground and not self.grappling:
            self.vel_y = Config.JUMP_FORCE
            self._set_anim('jumping')
            state.audio.play('jump')

    # ── Grapple ───────────────────────────────────────────────────────────
    def start_grapple(self):
        if self.grappling:
            return
        best, best_d = None, GRAPPLE_RANGE
        for ent in state.helicopters + state.shooting_drones:
            if not ent.enabled:
                continue
            d = distance(self.position, ent.position)
            if d < best_d:
                best_d, best = d, ent
        if best is None:
            return
        self.grapple_anchor = best
        self.rope_length    = best_d
        self.swing_angle    = math.atan2(self.y - best.y, self.x - best.x)
        self.angular_vel    = -self.vel_y / max(self.rope_length, 0.5)
        self.vel_y          = 0.0
        self.grappling      = True
        state.audio.play('grapple')

    def release_grapple(self):
        if not self.grappling:
            return
        self.vel_y          = self.angular_vel * self.rope_length * math.cos(self.swing_angle) * 1.3
        self.x              = PLAYER_X
        self.grappling      = False
        self.grapple_anchor = None
        state.clear_rope()

    # ── Update ────────────────────────────────────────────────────────────
    def update(self):
        if not self.alive or not state.game_running or state.paused:
            return

        if self.grappling:
            self._swing_update()
        else:
            self._gravity_update()

        # Ground clamp
        floor = GROUND_Y + self.scale_y / 2
        if self.y <= floor:
            self.y         = floor
            self.vel_y     = 0.0
            self.on_ground = True
            if self.grappling:
                self.release_grapple()
        else:
            self.on_ground = False

        self._check_hits()

        # Animation
        self._set_anim('jumping' if (self.grappling or not self.on_ground) else 'running')
        self.anim_timer += time.dt
        if self.anim_timer >= self.anim_speed:
            self.current_frame  = (self.current_frame + 1) % self.frame_counts[self.anim_state]
            self.anim_timer    -= self.anim_speed
            self._apply_frame()

    def _gravity_update(self):
        self.vel_y -= Config.GRAVITY * time.dt
        if self.vel_y > 0 and not held_keys['space']:
            self.vel_y -= Config.GRAVITY * (Config.LOW_JUMP_MULT - 1) * time.dt
        elif self.vel_y < 0:
            self.vel_y -= Config.GRAVITY * (Config.FALL_MULT - 1) * time.dt
        self.y += self.vel_y * time.dt

    def _swing_update(self):
        anchor = self.grapple_anchor
        if not anchor or not anchor.enabled:
            self.release_grapple()
            return
        # Pendulum: alpha = -(g/L) * sin(theta from vertical down)
        alpha            = -(Config.GRAVITY / self.rope_length) * math.sin(self.swing_angle + math.pi / 2)
        self.angular_vel  = self.angular_vel * 0.999 + alpha * time.dt
        self.swing_angle += self.angular_vel * time.dt
        self.x = anchor.x + self.rope_length * math.cos(self.swing_angle)
        self.y = anchor.y + self.rope_length * math.sin(self.swing_angle)
        state.update_rope(self, anchor)

    def _check_hits(self):
        # Late import avoids circular dependency with game.py
        from game import trigger_death, collect_coin
        hit = self.intersects()
        if not hit.hit:
            return
        name = getattr(hit.entity, 'name', '')
        if name == 'car':
            car_top = hit.entity.y + hit.entity.scale_y / 2
            if self.vel_y <= 0 and self.y - self.scale_y / 2 >= car_top - 0.4:
                self.y         = car_top + self.scale_y / 2
                self.vel_y     = 0.0
                self.on_ground = True
            else:
                trigger_death()
        elif name in ('drone_projectile', 'charging_drone'):
            trigger_death()
        elif name == 'coin':
            collect_coin(hit.entity)
