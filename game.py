"""
Entry point: game loop, spawning, game start/reset, input.
Run with: python game.py
"""
from ursina import *
import random, math

import state
import ui
from config import Config, PLAYER_X, GROUND_Y, CAMERA_OFFSET
from audio import AudioManager
from player import Player
from obstacles import Car, Coin, Helicopter
from enemies import ChargingDrone, ShootingDrone


# ── Game state functions ───────────────────────────────────────────────────
def trigger_death():
    if not state.game_running:
        return
    state.game_running = False
    state.audio.play('death')
    if state.score > state.high_score:
        state.high_score = int(state.score)
    state.player.alive = False
    state.clear_rope()
    ui.destroy_hud()
    ui.show_death_screen()


def collect_coin(coin_ent):
    state.score     += Config.COIN_VALUE
    state.num_coins += 1
    if coin_ent in state.coins_list:
        state.coins_list.remove(coin_ent)
    state._destroy(coin_ent)
    state.audio.play('coin')


def _reset_game():
    for lst in (state.cars, state.coins_list, state.helicopters,
                state.charging_drones, state.shooting_drones):
        for e in lst:
            state._destroy(e)
        lst.clear()
    state.clear_rope()
    state.score = state.elapsed = state.num_coins = 0.0
    state.scroll_speed   = Config.SCROLL_SPEED_BASE
    state.paused         = False
    state.game_running   = False
    if state.game_manager:
        state.game_manager.reset_timers()
    ui.destroy_hud()


def start_game():
    _reset_game()
    ui.create_hud()
    p            = state.player
    p.position   = Vec3(PLAYER_X, GROUND_Y + p.scale_y / 2, 0)
    p.vel_y      = 0.0
    p.on_ground  = True
    p.alive      = True
    p.grappling       = False
    p.grapple_anchor  = None
    p.enable()
    state.game_running = True
    state.audio.play_music()


# ── Input ─────────────────────────────────────────────────────────────────
def input(key):
    if key == 'escape':
        if state.game_running and not state.paused:
            ui.show_pause()
        elif state.paused:
            state.paused = False
            state._destroy(state.pause_panel); state.pause_panel = None
    if key == 'space' and state.game_running and not state.paused:
        state.player.do_jump()
    if key == 'f' and state.game_running and not state.paused:
        state.player.start_grapple()
    if key == 'f up':
        state.player.release_grapple()


# ── Game manager ──────────────────────────────────────────────────────────
class GameManager(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_timers()

    def reset_timers(self):
        self.car_t     = 0.0
        self.coin_t    = 0.0
        self.heli_t    = 0.0
        self.drone_c_t = 0.0
        self.drone_s_t = 0.0

    def _tick_spawn(self, attr, base, minimum, cls, lst):
        val = getattr(self, attr) + time.dt
        if val >= state._spawn_interval(base, minimum):
            val = 0.0
            lst.append(cls())
        setattr(self, attr, val)

    def _spawn_coins(self):
        self.coin_t += time.dt
        if self.coin_t >= state._spawn_interval(Config.COIN_SPAWN_BASE, Config.COIN_SPAWN_MIN):
            self.coin_t = 0.0
            x      = state._spawn_x()
            base_y = random.uniform(GROUND_Y + 1.5, GROUND_Y + 5)
            count  = random.randint(3, 6)
            for i in range(count):
                cx = x + i * 1.2
                cy = base_y + math.sin(i / count * math.pi) * 2
                state.coins_list.append(Coin(cx, cy))

    def update(self):
        if state.paused or not state.game_running:
            return

        state.elapsed     += time.dt
        state.scroll_speed = min(
            Config.SCROLL_SPEED_BASE + Config.SCROLL_RAMP * state.elapsed,
            Config.SCROLL_SPEED_MAX
        )
        state.score += Config.SCORE_PER_SEC * time.dt
        ui.update_hud()

        camera.x       = state.player.x + CAMERA_OFFSET
        state.ground.x = camera.x

        # Parallax — higher multiplier makes near layers feel faster
        for i, layer in enumerate(state.background_layers):
            spd = state.scroll_speed * 0.7 / (i + 1)
            for bg in layer:
                bg.x -= spd * time.dt
                if bg.x + bg.scale_x / 2 <= camera.x - camera.fov / 2 - bg.scale_x / 2:
                    bg.x += bg.scale_x * 2

        # Spawning
        self._tick_spawn('car_t',     Config.CAR_SPAWN_BASE,     Config.CAR_SPAWN_MIN,     Car,           state.cars)
        self._tick_spawn('heli_t',    Config.HELI_SPAWN_BASE,    Config.HELI_SPAWN_MIN,    Helicopter,    state.helicopters)
        self._tick_spawn('drone_c_t', Config.DRONE_C_SPAWN_BASE, Config.DRONE_C_SPAWN_MIN, ChargingDrone, state.charging_drones)
        self._tick_spawn('drone_s_t', Config.DRONE_S_SPAWN_BASE, Config.DRONE_S_SPAWN_MIN, ShootingDrone, state.shooting_drones)
        self._spawn_coins()


# ── Setup ─────────────────────────────────────────────────────────────────
def main():
    app = Ursina()
    window.title      = 'Spaghetti Bandit'
    window.borderless = False
    window.size       = Vec2(1280, 720)
    window.color      = color.rgb(135, 206, 235)

    camera.orthographic = True
    camera.fov          = 30   # wider view so player can see further ahead

    state.audio = AudioManager()

    state.ground = Entity(
        model='quad', color=color.green,
        scale=(1000, 1),
        position=(0, GROUND_Y, 0),
        collider='box', name='ground'
    )

    # Heights and y-offsets scaled up to fill the wider FOV=30 viewport
    bg_defs = [
        (400, 32, 5,   16),
        (360, 29, 4,   14),
        (320, 26, 3,   13),
        (280, 23, 2,   11),
        (240, 20, 1,    9),
        (200, 17, 0.5,  8),
    ]
    state.background_layers = []
    for idx, (w, h, z, y_off) in enumerate(bg_defs):
        img = f'assets/images/{idx + 1}.png'
        y   = GROUND_Y + 0.5 + y_off
        state.background_layers.append([
            Entity(model='quad', texture=img, scale=(w, h), z=z, x=-w/2, y=y),
            Entity(model='quad', texture=img, scale=(w, h), z=z, x= w/2, y=y),
        ])

    state.player      = Player()
    state.game_manager = GameManager()

    ui.show_main_menu()
    app.run()


if __name__ == '__main__':
    main()
