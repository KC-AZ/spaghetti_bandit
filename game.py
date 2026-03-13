"""
Entry point: game loop, level loading, input, camera.
Run with: python game.py
"""
from ursina import *
import state
import ui
from config import GROUND_Y, CAMERA_OFFSET
from audio import AudioManager
from player import Player
from obstacles import Coin, Helicopter
from enemies import ChargingDrone, ShootingDrone
from level_data import LEVELS


# ── Death / coin / level complete ──────────────────────────────────────────
def trigger_death():
    if not state.game_running:
        return
    state.game_running = False
    state.audio.play('death')
    state.player.alive = False
    state.clear_rope()
    ui.destroy_hud()
    ui.show_death_screen()


def collect_coin(coin_ent):
    state.num_coins += 1
    if coin_ent in state.coins_list:
        state.coins_list.remove(coin_ent)
    state._destroy(coin_ent)
    state.audio.play('coin')


def complete_level():
    if not state.game_running or state.level_complete:
        return
    state.level_complete = True
    state.game_running   = False
    state.clear_rope()

    lvl_id = state.current_level
    t      = state.level_timer
    old_pb = state.pbs.get(lvl_id)
    is_pb  = old_pb is None or t < old_pb
    if is_pb:
        state.pbs[lvl_id] = t
        state.save_pbs()

    state.audio.play('coin')
    ui.destroy_hud()
    ui.show_level_complete(t, state.pbs.get(lvl_id), is_pb, lvl_id)


# ── Level management ───────────────────────────────────────────────────────
def _clear_level_entities():
    for lst in (state.cars, state.coins_list, state.helicopters,
                state.charging_drones, state.shooting_drones,
                state.drone_projectiles):
        for e in lst:
            state._destroy(e)
        lst.clear()
    state._destroy(state.finish_line)
    state.finish_line = None
    state.clear_rope()


def load_level(level_id):
    _clear_level_entities()
    ui.destroy_hud()

    level = LEVELS[level_id - 1]
    state.current_level  = level_id
    state.level_timer    = 0.0
    state.level_complete = False
    state.num_coins      = 0

    window.color = color.rgb32(*level['sky_color'])

    for h in level.get('helicopters', []):
        state.helicopters.append(Helicopter(h['x'], h['y']))
    for d in level.get('charging_drones', []):
        state.charging_drones.append(ChargingDrone(d['x'], d['y']))
    for d in level.get('shooting_drones', []):
        state.shooting_drones.append(ShootingDrone(d['x'], d['y']))
    for c in level.get('coins', []):
        state.coins_list.append(Coin(c['x'], c['y']))

    # Finish line — tall gold stripe at the end of the level
    state.finish_line = Entity(
        model='quad', color=color.gold,
        scale=(1.0, 24),
        position=(level['length'], GROUND_Y + 12, 0),
        collider='box', name='finish_line',
        z=0.1
    )

    # Reset player
    p           = state.player
    floor_y     = GROUND_Y + 0.5 + p.scale_y / 2
    p.position  = Vec3(0, floor_y, 0)
    p.vel_x     = 0.0
    p.vel_y     = 0.0
    p.on_ground = True
    p.ducking   = False
    p.scale_y   = 3.0
    p.face_dir  = 1
    p.alive     = True
    p.grappling       = False
    p.grapple_anchor  = None
    p.rope_taut       = False
    p.jumps_remaining = 2
    p.jump_buffer     = 0.0
    p.coyote_timer    = 0.0
    p.parry_active    = False
    p.parry_timer     = 0.0
    p.parry_cooldown  = 0.0
    p.color           = color.white
    p.enable()

    # Camera
    camera.x = p.x + CAMERA_OFFSET

    # Background — reset parallax starting positions around player
    for i, layer in enumerate(state.background_layers):
        w = layer[0].scale_x
        layer[0].x = camera.x - w / 2
        layer[1].x = camera.x + w / 2

    if state.game_manager:
        state.game_manager.prev_camera_x = camera.x

    ui.create_hud()
    state.game_running = True


def start_game(level_id=1):
    load_level(level_id)
    state.audio.play_music()


def restart_level():
    state._destroy(state.level_complete_panel)
    state.level_complete_panel = None
    load_level(state.current_level)


# ── Input ──────────────────────────────────────────────────────────────────
def input(key):
    if key == 'escape':
        if state.game_running and not state.paused:
            ui.show_pause()
        elif state.paused:
            state.paused = False
            state._destroy(state.pause_panel)
            state.pause_panel = None

    if key == 'space' and state.game_running and not state.paused:
        state.player.do_jump()

    if key in ('left shift', 'right shift', 'shift') and state.game_running and not state.paused:
        state.player.start_grapple()
    if key in ('left shift up', 'right shift up', 'shift up'):
        state.player.release_grapple()

    if key == 'f' and state.game_running and not state.paused:
        state.player.do_parry()

    # Quick restart
    if key == 'r' and not state.paused and (state.game_running or state.level_complete):
        restart_level()


# ── Game manager (camera, timer, parallax) ─────────────────────────────────
class GameManager(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prev_camera_x = 0.0

    def update(self):
        if state.paused or not state.game_running:
            return

        state.level_timer += time.dt
        ui.update_hud()

        # Finish line — position check is reliable in orthographic 2D
        if (state.finish_line and
                state.player.x >= state.finish_line.x - state.finish_line.scale_x / 2):
            complete_level()
            return

        # Camera follows player
        camera.x       = state.player.x + CAMERA_OFFSET
        state.ground.x = camera.x

        # Parallax — driven by how much the camera moved this frame
        dx = camera.x - self.prev_camera_x
        for i, layer in enumerate(state.background_layers):
            factor = 0.12 * (i + 1)   # near layers move more
            for bg in layer:
                bg.x -= dx * factor
                # Wrap tile when it drifts fully off the left or right
                if bg.x + bg.scale_x / 2 < camera.x - bg.scale_x:
                    bg.x += bg.scale_x * 2
                elif bg.x - bg.scale_x / 2 > camera.x + bg.scale_x:
                    bg.x -= bg.scale_x * 2
        self.prev_camera_x = camera.x


# ── Setup ──────────────────────────────────────────────────────────────────
def main():
    # When frozen as a PyInstaller exe, switch to the _internal bundle dir so
    # relative asset paths (assets/images/1.png etc.) resolve correctly.
    import sys
    if getattr(sys, 'frozen', False):
        import os as _os
        _os.chdir(sys._MEIPASS)

    app = Ursina()
    window.title      = 'Spaghetti Bandit'
    window.borderless = False
    window.size       = Vec2(1280, 720)
    window.color      = color.rgb32(135, 206, 235)

    camera.orthographic = True
    camera.fov          = 30

    state.audio = AudioManager()
    state.load_pbs()

    state.ground = Entity(
        model='quad', color=color.green,
        scale=(2000, 1),
        position=(0, GROUND_Y, 0),
        collider='box', name='ground'
    )

    bg_defs = [
        (400, 32, 5,  16),
        (360, 29, 4,  14),
        (320, 26, 3,  13),
        (280, 23, 2,  11),
        (240, 20, 1,   9),
        (200, 17, 0.5, 8),
    ]
    state.background_layers = []
    for idx, (w, h, z, y_off) in enumerate(bg_defs):
        img = f'assets/images/{idx + 1}.png'
        y   = GROUND_Y + 0.5 + y_off
        state.background_layers.append([
            Entity(model='quad', texture=img, scale=(w, h), z=z, x=-w/2, y=y),
            Entity(model='quad', texture=img, scale=(w, h), z=z, x= w/2, y=y),
        ])

    state.player       = Player()
    state.player.disable()
    state.game_manager = GameManager()

    ui.show_main_menu()
    app.run()


if __name__ == '__main__':
    main()
