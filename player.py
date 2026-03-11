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
            position=(PLAYER_X, GROUND_Y + 2.0),
            collider='box',
            name='player',
            z=0
        )
        _bbox = [Vec3(-.2,-.5,0), Vec3(.2,-.5,0), Vec3(.2,.5,0), Vec3(-.2,.5,0), Vec3(-.2,-.5,0)]
        Entity(parent=self, model=Mesh(vertices=_bbox, mode='line', thickness=2),
               color=color.lime, unlit=True, z=-0.05)

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

        self.vel_x           = 0.0
        self.vel_y           = 0.0
        self.on_ground       = False
        self.alive           = True
        self.jumps_remaining = 2
        self.jump_buffer     = 0.0   # bhop input buffer timer
        self.coyote_timer    = 0.0   # grace window after leaving ground

        # Grapple state
        self.grappling      = False
        self.grapple_anchor = None
        self.rope_length    = 0.0
        self.swing_angle    = 0.0   # radians from anchor (0 = right, -pi/2 = below)
        self.angular_vel    = 0.0
        self.entry_vel_x    = 0.0   # vel_x when grapple attached
        self.min_swing_y    = 0.0   # lowest y reached this swing

        # Parry state
        self.parry_active   = False
        self.parry_timer    = 0.0
        self.parry_cooldown = 0.0

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

    # ── Parry ─────────────────────────────────────────────────────────────
    def do_parry(self):
        if self.parry_cooldown > 0 or not state.game_running or state.paused:
            return
        self.parry_active   = True
        self.parry_timer    = 1.5
        self.parry_cooldown = 3.0

    def _update_parry(self):
        if self.parry_cooldown > 0:
            self.parry_cooldown = max(0.0, self.parry_cooldown - time.dt)
        if self.parry_active:
            self.color = color.cyan
            self.parry_timer -= time.dt
            if self.parry_timer <= 0:
                self.parry_active = False
            else:
                for proj in list(state.drone_projectiles):
                    if distance(self.position, proj.position) < 4:
                        proj.dir = -proj.dir
                        proj.color = color.red
        elif self.parry_cooldown > 0:
            self.color = color.rgb(160, 160, 160)   # grey = on cooldown
        else:
            self.color = color.white                 # white = ready

    # ── Jump ──────────────────────────────────────────────────────────────
    def _execute_jump(self, bhop=False):
        # Second jump (jumps_remaining == 1) is weaker than the first
        self.vel_y           = Config.DOUBLE_JUMP_FORCE if self.jumps_remaining == 1 else Config.JUMP_FORCE
        self.jumps_remaining -= 1
        if bhop:
            # Diminishing returns: boost shrinks as vel_x approaches the cap
            boost      = Config.BHOP_BOOST * (1.0 - self.vel_x / Config.BHOP_MAX_VEL_X)
            self.vel_x = min(self.vel_x + max(boost, 0.0), Config.BHOP_MAX_VEL_X)
        self._set_anim('jumping')
        state.audio.play('jump')

    def do_jump(self):
        if self.grappling:
            return
        if not self.on_ground:
            # Any airborne press buffers a bhop — easy timing
            self.jump_buffer = Config.BHOP_BUFFER
        if self.jumps_remaining > 0:
            self._execute_jump()

    # ── Grapple ───────────────────────────────────────────────────────────
    def start_grapple(self):
        if self.grappling:
            return
        best, best_d = None, GRAPPLE_RANGE
        for ent in state.helicopters:
            if not ent.enabled:
                continue
            if ent.x <= self.x:          # only target anchors ahead (to the right)
                continue
            d = distance(self.position, ent.position)
            if d < best_d:
                best_d, best = d, ent
        if best is None:
            return
        self.grapple_anchor = best
        self.rope_length    = best_d
        self.swing_angle    = math.atan2(self.y - best.y, self.x - best.x)
        # In the anchor's frame the player moves rightward at scroll_speed (world scrolls left).
        # That relative motion is what drives the swing arc.
        rel_vel_x = self.vel_x + state.scroll_speed
        rel_vel_y = self.vel_y
        tang_vel         = (rel_vel_x * (-math.sin(self.swing_angle)) +
                            rel_vel_y *   math.cos(self.swing_angle))
        self.angular_vel  = tang_vel / max(self.rope_length, 0.5)
        self.entry_vel_x  = self.vel_x   # preserved as momentum floor on release
        self.min_swing_y  = self.y       # tracks lowest point reached during swing
        self.vel_x        = 0.0
        self.vel_y        = 0.0
        self.grappling    = True
        state.audio.play('grapple')

    def release_grapple(self):
        if not self.grappling:
            return
        tang_speed  = self.angular_vel * self.rope_length
        swing_vel_x = tang_speed * (-math.sin(self.swing_angle))
        swing_vel_y = tang_speed *   math.cos(self.swing_angle)

        # If the player releases before passing the lowest point, guarantee they
        # exit at least as fast as they entered. Past the bottom is on them.
        past_lowest = self.y > self.min_swing_y + 2.0
        if not past_lowest:
            self.vel_x = max(swing_vel_x, self.entry_vel_x)
        else:
            self.vel_x = swing_vel_x
        self.vel_y          = swing_vel_y
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

        # Ground clamp — ground top is at GROUND_Y + 0.5
        floor = GROUND_Y + 0.5 + self.scale_y / 2
        if self.y <= floor:
            self.y               = floor
            self.vel_y           = 0.0
            self.on_ground       = True
            self.jumps_remaining = 2
            self.coyote_timer    = Config.COYOTE_TIME
            if self.grappling:
                self.release_grapple()
            elif self.jump_buffer > 0:
                self.jump_buffer = 0.0
                self._execute_jump(bhop=True)
        else:
            self.on_ground    = False
            self.coyote_timer = max(0.0, self.coyote_timer - time.dt)
            self.jump_buffer  = max(0.0, self.jump_buffer  - time.dt)
            # Coyote bhop: just left the ground, buffer already queued
            if self.coyote_timer > 0 and self.jump_buffer > 0 and not self.grappling:
                self.jump_buffer  = 0.0
                self.coyote_timer = 0.0
                self._execute_jump(bhop=True)

        self._update_parry()
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
        if self.vel_y < 0:
            self.vel_y -= Config.GRAVITY * (Config.FALL_MULT - 1) * time.dt
        self.y += self.vel_y * time.dt

        # Heavy ground friction (like Source) bleeds speed unless you bhop;
        # low air drag lets momentum carry between jumps and grapples.
        drag = Config.GROUND_FRICTION if self.on_ground else Config.GRAPPLE_X_DRAG
        self.vel_x -= self.vel_x * drag * time.dt
        self.vel_x  = max(0.0, self.vel_x)   # never slide backward
        self.x     += self.vel_x * time.dt

    def _swing_update(self):
        anchor = self.grapple_anchor
        if not anchor or not anchor.enabled:
            self.release_grapple()
            return

        # Reel in toward anchor until minimum rope length
        if self.rope_length > Config.GRAPPLE_MIN_ROPE:
            old_L = self.rope_length
            self.rope_length = max(Config.GRAPPLE_MIN_ROPE,
                                   self.rope_length - Config.GRAPPLE_REEL_SPEED * time.dt)
            # Conserve angular momentum: ω * L = const → ω increases as L shrinks
            self.angular_vel *= old_L / self.rope_length

        self.min_swing_y = min(self.min_swing_y, self.y)

        # Pendulum with boosted gravity for a snappier, faster swing
        alpha            = -(Config.GRAVITY * Config.GRAPPLE_SWING_MULT / self.rope_length) * math.sin(self.swing_angle + math.pi / 2)
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
                self.y               = car_top + self.scale_y / 2
                self.vel_y           = 0.0
                self.on_ground       = True
                self.jumps_remaining = 2
            else:
                trigger_death()
        elif name == 'drone_projectile':
            if not self.parry_active:
                trigger_death()
        elif name == 'charging_drone':
            trigger_death()
        elif name == 'coin':
            collect_coin(hit.entity)
