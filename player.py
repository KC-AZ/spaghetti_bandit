"""
Player entity: movement, jump, grapple swing, animation, collision.
Controls: A/D = walk, S = duck, Space = jump, Shift = grapple, F = parry
"""
from ursina import *
import math
import state
from config import Config, GROUND_Y, GRAPPLE_RANGE


class Player(Entity):
    def __init__(self):
        super().__init__(
            model='quad',
            texture=load_texture('idle.png'),
            scale=(3, 3),
            position=(0, GROUND_Y + 2.0),
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

        # Physics
        self.vel_x           = 0.0
        self.vel_y           = 0.0
        self.face_dir        = 1       # 1 = right, -1 = left
        self.on_ground       = False
        self.ducking         = False
        self.alive           = True
        self.jumps_remaining = 2
        self.jump_buffer     = 0.0
        self.coyote_timer    = 0.0

        # Grapple
        self.grappling      = False
        self.grapple_anchor = None
        self.rope_length    = 0.0
        self.rope_taut      = False
        self.swing_angle    = 0.0
        self.angular_vel    = 0.0
        self.entry_vel_x    = 0.0
        self.min_swing_y    = 0.0

        # Parry
        self.parry_active   = False
        self.parry_timer    = 0.0
        self.parry_cooldown = 0.0

    # ── Animation ──────────────────────────────────────────────────────────
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

    # ── Parry ──────────────────────────────────────────────────────────────
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
            self.color = color.rgb32(160, 160, 160)   # grey = on cooldown
        else:
            self.color = color.white                 # white = ready

    # ── Jump ───────────────────────────────────────────────────────────────
    def _execute_jump(self, bhop=False):
        self.vel_y           = Config.DOUBLE_JUMP_FORCE if self.jumps_remaining == 1 else Config.JUMP_FORCE
        self.jumps_remaining -= 1
        if bhop:
            boost      = Config.BHOP_BOOST * (1.0 - self.vel_x / Config.BHOP_MAX_VEL_X)
            self.vel_x = min(self.vel_x + max(boost, 0.0), Config.BHOP_MAX_VEL_X)
        self._set_anim('jumping')
        state.audio.play('jump')

    def do_jump(self):
        if self.grappling:
            return
        if not self.on_ground:
            self.jump_buffer = Config.BHOP_BUFFER
        if self.jumps_remaining > 0:
            self._execute_jump()

    # ── Duck ───────────────────────────────────────────────────────────────
    def _handle_duck(self):
        want_duck = held_keys['s'] and self.on_ground and not self.grappling
        if want_duck == self.ducking:
            return
        self.ducking = want_duck
        if self.ducking:
            self.scale_y = 1.5
            if self.on_ground:
                self.y = GROUND_Y + 0.5 + 0.75    # GROUND_Y + 0.5 + scale_y/2
        else:
            self.scale_y = 3.0
            if self.on_ground:
                self.y = GROUND_Y + 0.5 + 1.5     # GROUND_Y + 0.5 + scale_y/2

    # ── Grapple ────────────────────────────────────────────────────────────
    def start_grapple(self):
        if self.grappling:
            return
        best, best_d = None, GRAPPLE_RANGE
        for ent in state.helicopters:
            if not ent.enabled:
                continue
            if ent.x <= self.x:
                continue
            d = distance(self.position, ent.position)
            if d < best_d:
                best_d, best = d, ent
        if best is None:
            return
        self.grapple_anchor = best
        self.rope_length    = min(best_d, Config.GRAPPLE_SLACK_MAX)
        self.grappling      = True

        if self.on_ground:
            # Skip slack phase when standing — go taut immediately so the pendulum
            # repositions the player above the floor before the ground clamp fires
            dx = self.x - best.x
            dy = self.y - best.y
            self.rope_length = best_d
            self.swing_angle = math.atan2(dy, dx)
            tang_vel   = (self.vel_x * (-math.sin(self.swing_angle)) +
                          self.vel_y *   math.cos(self.swing_angle))
            radial_vel = (self.vel_x *   math.cos(self.swing_angle) +
                          self.vel_y *   math.sin(self.swing_angle))
            tang_vel  += max(0.0, -radial_vel) * 0.4
            self.angular_vel = tang_vel / max(best_d, 0.5)
            self.entry_vel_x = self.vel_x
            self.min_swing_y = self.y
            self.vel_x       = 0.0
            self.vel_y       = 0.0
            self.rope_taut   = True
            # Nudge above floor so the ground clamp doesn't release us this frame
            floor = GROUND_Y + 0.5 + self.scale_y / 2
            self.y = max(self.y, floor + 0.15)
        else:
            self.rope_taut = False   # rope starts slack; vel_x/vel_y untouched

        state.audio.play('grapple')

    def release_grapple(self):
        if not self.grappling:
            return
        if self.rope_taut:
            tang_speed  = self.angular_vel * self.rope_length
            swing_vel_x = tang_speed * (-math.sin(self.swing_angle))
            swing_vel_y = tang_speed *   math.cos(self.swing_angle)
            past_lowest = self.y > self.min_swing_y + 2.0
            if not past_lowest:
                self.vel_x = max(swing_vel_x, self.entry_vel_x)
            else:
                self.vel_x = swing_vel_x
            self.vel_y = swing_vel_y
        # if still slack, vel_x/vel_y are already correct from free flight
        self.grappling      = False
        self.rope_taut      = False
        self.grapple_anchor = None
        state.clear_rope()

    # ── Update ─────────────────────────────────────────────────────────────
    def update(self):
        if not self.alive or not state.game_running or state.paused:
            return

        self._handle_duck()

        if self.grappling:
            self._swing_update()
        else:
            self._gravity_update()

        # Ground clamp
        floor = GROUND_Y + 0.5 + self.scale_y / 2
        if self.y <= floor:
            self.y               = floor
            self.vel_y           = 0.0
            self.on_ground       = True
            self.jumps_remaining = 2
            self.coyote_timer    = Config.COYOTE_TIME
            if self.grappling and self.rope_taut:
                self.release_grapple()
            elif self.jump_buffer > 0:
                self.jump_buffer = 0.0
                self._execute_jump(bhop=True)
        else:
            self.on_ground    = False
            self.coyote_timer = max(0.0, self.coyote_timer - time.dt)
            self.jump_buffer  = max(0.0, self.jump_buffer  - time.dt)
            if self.coyote_timer > 0 and self.jump_buffer > 0 and not self.grappling:
                self.jump_buffer  = 0.0
                self.coyote_timer = 0.0
                self._execute_jump(bhop=True)

        self._update_parry()
        self._check_hits()

        # Animation
        walk_input = (held_keys['d'] - held_keys['a']) if not self.grappling else 0
        if self.grappling or not self.on_ground:
            anim = 'jumping'
        elif abs(walk_input) > 0 or self.vel_x > 0.5:
            anim = 'running'
        else:
            anim = 'idle'
        self._set_anim(anim)

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

        # Horizontal: walk input + bhop momentum
        walk_input = held_keys['d'] - held_keys['a']
        speed      = Config.DUCK_SPEED if self.ducking else Config.WALK_SPEED
        self.x    += walk_input * speed * time.dt

        # Update facing direction from walk input
        if walk_input > 0:
            self.face_dir = 1
        elif walk_input < 0:
            self.face_dir = -1
        self.scale_x = self.face_dir * abs(self.scale_x)

        # Bhop momentum drag
        drag       = Config.GROUND_FRICTION if self.on_ground else Config.GRAPPLE_X_DRAG
        self.vel_x = max(0.0, self.vel_x - self.vel_x * drag * time.dt)
        self.x    += self.vel_x * time.dt

    def _swing_update(self):
        anchor = self.grapple_anchor
        if not anchor or not anchor.enabled:
            self.release_grapple()
            return

        if not self.rope_taut:
            # Slack phase: free flight under gravity — velocity fully preserved
            self.vel_y -= Config.GRAVITY * time.dt
            if self.vel_y < 0:
                self.vel_y -= Config.GRAVITY * (Config.FALL_MULT - 1) * time.dt
            self.x += self.vel_x * time.dt
            self.y += self.vel_y * time.dt
            self.vel_x = max(0.0, self.vel_x - self.vel_x * Config.GRAPPLE_X_DRAG * time.dt)

            dx = self.x - anchor.x
            dy = self.y - anchor.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist >= self.rope_length:
                # Rope snaps taut — convert velocity to angular now
                self.rope_length = dist
                self.swing_angle = math.atan2(dy, dx)
                tang_vel   = (self.vel_x * (-math.sin(self.swing_angle)) +
                              self.vel_y *   math.cos(self.swing_angle))
                radial_vel = (self.vel_x *   math.cos(self.swing_angle) +
                              self.vel_y *   math.sin(self.swing_angle))
                # Redirect 40% of any outward radial speed into the swing
                tang_vel  += max(0.0, -radial_vel) * 0.4
                self.angular_vel = tang_vel / max(self.rope_length, 0.5)
                self.entry_vel_x = self.vel_x
                self.min_swing_y = self.y
                self.vel_x       = 0.0
                self.vel_y       = 0.0
                self.rope_taut   = True
            state.update_rope(self, anchor)
            return

        # Taut pendulum physics — reel in unless already close to the helicopter
        if self.rope_length > Config.GRAPPLE_REEL_MIN_LENGTH:
            old_L            = self.rope_length
            self.rope_length = max(Config.GRAPPLE_REEL_MIN_LENGTH,
                                   self.rope_length - Config.GRAPPLE_REEL_SPEED * time.dt)
            self.angular_vel *= old_L / self.rope_length

        self.min_swing_y = min(self.min_swing_y, self.y)

        alpha            = -(Config.GRAVITY * Config.GRAPPLE_SWING_MULT / self.rope_length) * math.sin(self.swing_angle + math.pi / 2)
        self.angular_vel  = self.angular_vel * 0.999 + alpha * time.dt
        self.swing_angle += self.angular_vel * time.dt
        self.x = anchor.x + self.rope_length * math.cos(self.swing_angle)
        self.y = anchor.y + self.rope_length * math.sin(self.swing_angle)
        state.update_rope(self, anchor)

    def _check_hits(self):
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
