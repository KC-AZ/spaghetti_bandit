"""
All UI: HUD, main menu, settings, pause screen, death screen.
"""
from ursina import *
import state
from state import _destroy


# ── HUD ───────────────────────────────────────────────────────────────────
def create_hud():
    state.hud_score_text = Text('Score: 0', origin=(-0.5, 0.5),
                                position=(-0.85, 0.47), scale=1.4, color=color.white)
    state.hud_coins_text = Text('Coins: 0', origin=(-0.5, 0.5),
                                position=(-0.85, 0.39), scale=1.4, color=color.yellow)

def update_hud():
    if state.hud_score_text: state.hud_score_text.text = f'Score: {int(state.score)}'
    if state.hud_coins_text: state.hud_coins_text.text = f'Coins: {state.num_coins}'

def destroy_hud():
    _destroy(state.hud_score_text); state.hud_score_text = None
    _destroy(state.hud_coins_text); state.hud_coins_text = None


# ── Main menu ─────────────────────────────────────────────────────────────
def show_main_menu():
    _destroy(state.menu_panel)
    state.menu_panel = Entity(parent=camera.ui, model='quad',
                              color=color.rgba(0, 0, 0, 200), scale=(2, 2), z=-1)
    Text('SPAGHETTI BANDIT', parent=state.menu_panel, y=0.36, scale=3,
         color=color.orange, origin=(0, 0))
    if state.high_score > 0:
        Text(f'Best: {state.high_score}', parent=state.menu_panel, y=0.23, scale=1.3,
             color=color.white, origin=(0, 0))
    Text('SPACE – Jump   |   F (hold) – Grapple', parent=state.menu_panel,
         y=0.10, scale=0.9, color=color.gray, origin=(0, 0))

    def _play():
        from game import start_game
        _destroy(state.menu_panel); state.menu_panel = None
        start_game()

    def _settings():
        _destroy(state.menu_panel); state.menu_panel = None
        show_settings(back_fn=show_main_menu)

    Button('Play',     parent=state.menu_panel, scale=(0.25, 0.1), y=-0.06, on_click=_play)
    Button('Settings', parent=state.menu_panel, scale=(0.25, 0.1), y=-0.20, on_click=_settings)
    Button('Quit',     parent=state.menu_panel, scale=(0.25, 0.1), y=-0.34, on_click=application.quit)


# ── Settings ──────────────────────────────────────────────────────────────
def show_settings(back_fn=None):
    _destroy(state.settings_panel)
    state.settings_panel = Entity(parent=camera.ui, model='quad',
                                  color=color.rgba(20, 20, 20, 230), scale=(0.95, 0.95), z=-2)
    Text('Settings', parent=state.settings_panel, y=0.40, scale=2.2, origin=(0, 0))

    Text('Display', parent=state.settings_panel, y=0.28, scale=1.1,
         color=color.light_gray, origin=(0, 0))
    Button('Fullscreen', parent=state.settings_panel, scale=(0.38, 0.09), y=0.17,
           on_click=lambda: (setattr(window, 'fullscreen', True),
                             setattr(window, 'borderless', False)))
    Button('Borderless Fullscreen', parent=state.settings_panel, scale=(0.38, 0.09), y=0.06,
           on_click=lambda: (setattr(window, 'fullscreen', False),
                             setattr(window, 'borderless', True)))
    Button('1280×720 Windowed', parent=state.settings_panel, scale=(0.38, 0.09), y=-0.05,
           on_click=lambda: (setattr(window, 'fullscreen', False),
                             setattr(window, 'size', Vec2(1280, 720))))

    Text('Audio', parent=state.settings_panel, y=-0.17, scale=1.1,
         color=color.light_gray, origin=(0, 0))
    Text('Import MP3s into assets/audio/ to enable', parent=state.settings_panel,
         y=-0.25, scale=0.65, color=color.gray, origin=(0, 0))
    # TODO: connect .on_value_changed to state.audio.music_vol / state.audio.sfx_vol
    Slider(min=0, max=1, default=0.7, text='Music', parent=state.settings_panel,
           position=(-0.22, -0.31), scale=0.55)
    Slider(min=0, max=1, default=1.0, text='SFX',   parent=state.settings_panel,
           position=(-0.22, -0.41), scale=0.55)

    def _back():
        _destroy(state.settings_panel); state.settings_panel = None
        if back_fn:
            back_fn()

    Button('Back', parent=state.settings_panel, scale=(0.3, 0.09), y=-0.54, on_click=_back)


# ── Pause ─────────────────────────────────────────────────────────────────
def show_pause():
    state.paused = True
    _destroy(state.pause_panel)
    state.pause_panel = Entity(parent=camera.ui, model='quad',
                               color=color.rgba(0, 0, 0, 180), scale=(0.72, 0.72), z=-1)
    Text('PAUSED', parent=state.pause_panel, y=0.28, scale=2.5, origin=(0, 0))

    def _resume():
        state.paused = False
        _destroy(state.pause_panel); state.pause_panel = None

    def _to_menu():
        from game import _reset_game
        state.paused = False
        _destroy(state.pause_panel); state.pause_panel = None
        _reset_game()
        show_main_menu()

    Button('Resume',    parent=state.pause_panel, scale=(0.33, 0.1), y=0.08,  on_click=_resume)
    Button('Settings',  parent=state.pause_panel, scale=(0.33, 0.1), y=-0.07,
           on_click=lambda: show_settings(back_fn=show_pause))
    Button('Main Menu', parent=state.pause_panel, scale=(0.33, 0.1), y=-0.22, on_click=_to_menu)


# ── Death screen ──────────────────────────────────────────────────────────
def show_death_screen():
    _destroy(state.death_panel)
    state.death_panel = Entity(parent=camera.ui, model='quad',
                               color=color.rgba(0, 0, 0, 210), scale=(0.88, 0.68), z=-1)
    Text('GAME OVER', parent=state.death_panel, y=0.26,  scale=3,   color=color.red,   origin=(0, 0))
    Text(f'Score:  {int(state.score)}',      parent=state.death_panel, y=0.09,  scale=1.6, color=color.white, origin=(0, 0))
    Text(f'Best:   {int(state.high_score)}', parent=state.death_panel, y=-0.02, scale=1.3, color=color.cyan,  origin=(0, 0))

    def _restart():
        from game import start_game
        _destroy(state.death_panel); state.death_panel = None
        start_game()

    def _menu():
        from game import _reset_game
        _destroy(state.death_panel); state.death_panel = None
        _reset_game()
        show_main_menu()

    Button('Restart',   parent=state.death_panel, scale=(0.3, 0.1), y=-0.17, on_click=_restart)
    Button('Main Menu', parent=state.death_panel, scale=(0.3, 0.1), y=-0.30, on_click=_menu)
