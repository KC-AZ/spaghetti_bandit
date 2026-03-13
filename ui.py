"""
All UI: HUD, main menu, level select, settings, pause, death, level complete.
"""
from ursina import *
import state
from state import _destroy


# ── Time formatting ────────────────────────────────────────────────────────
def _fmt(t):
    if t is None:
        return '--:--.--'
    mins = int(t) // 60
    secs = t % 60
    return f'{mins}:{secs:05.2f}' if mins > 0 else f'{secs:.2f}'


# ── HUD ────────────────────────────────────────────────────────────────────
def create_hud():
    from level_data import LEVELS
    lvl  = LEVELS[state.current_level - 1]
    pb   = state.pbs.get(state.current_level)
    goal = lvl.get('baseline_time')

    state.hud_timer_text = Text('0.00', origin=(0, 0.5),
                                position=(0, 0.47), scale=2.2, color=color.white)
    state.hud_level_text = Text(lvl['name'], origin=(-0.5, 0.5),
                                position=(-0.85, 0.47), scale=1.1, color=color.orange)
    state.hud_coins_text = Text(f'PB: {_fmt(pb)}', origin=(0.5, 0.5),
                                position=(0.85, 0.485), scale=1.0, color=color.cyan)
    state.hud_goal_text  = Text(f'GOAL: {_fmt(goal)}', origin=(0.5, 0.5),
                                position=(0.85, 0.415), scale=1.0, color=color.yellow)
    state.hud_parry_text = Text('PARRY: READY', origin=(-0.5, -0.5),
                                position=(-0.85, -0.44), scale=0.9, color=color.lime)

def update_hud():
    if state.hud_timer_text:
        state.hud_timer_text.text = _fmt(state.level_timer)
    if state.hud_parry_text and state.player:
        p = state.player
        if p.parry_active:
            state.hud_parry_text.text  = 'PARRY: ACTIVE'
            state.hud_parry_text.color = color.cyan
        elif p.parry_cooldown > 0:
            state.hud_parry_text.text  = f'PARRY: {p.parry_cooldown:.1f}s'
            state.hud_parry_text.color = color.gray
        else:
            state.hud_parry_text.text  = 'PARRY: READY'
            state.hud_parry_text.color = color.lime

def destroy_hud():
    for attr in ('hud_bg', 'hud_timer_text', 'hud_level_text',
                 'hud_coins_text', 'hud_goal_text', 'hud_parry_text'):
        _destroy(getattr(state, attr, None))
        try:
            setattr(state, attr, None)
        except Exception:
            pass


# ── Main menu ──────────────────────────────────────────────────────────────
def show_main_menu():
    _destroy(state.menu_panel)
    state.menu_panel = Entity(parent=camera.ui, model='quad',
                              color=color.rgba(0, 0, 0, 200), scale=(2, 2), z=-1)
    Text('SPAGHETTI BANDIT', parent=state.menu_panel, y=0.36, scale=3,
         color=color.orange, origin=(0, 0))
    Text('A/D – Move   |   S – Duck   |   Space – Jump',
         parent=state.menu_panel, y=0.22, scale=0.85, color=color.gray, origin=(0, 0))
    Text('Shift – Grapple   |   F – Parry',
         parent=state.menu_panel, y=0.14, scale=0.85, color=color.gray, origin=(0, 0))

    def _levels():
        _destroy(state.menu_panel); state.menu_panel = None
        show_level_select()

    def _settings():
        _destroy(state.menu_panel); state.menu_panel = None
        show_settings(back_fn=show_main_menu)

    Button('Play',     parent=state.menu_panel, scale=(0.25, 0.1), y=0.00, on_click=_levels)
    Button('Settings', parent=state.menu_panel, scale=(0.25, 0.1), y=-0.14, on_click=_settings)
    Button('Quit',     parent=state.menu_panel, scale=(0.25, 0.1), y=-0.28, on_click=application.quit)


# ── Level select ───────────────────────────────────────────────────────────
def show_level_select():
    from level_data import LEVELS
    _destroy(state.level_select_panel)
    state.level_select_panel = Entity(parent=camera.ui, model='quad',
                                      color=color.rgba(0, 0, 0, 200), scale=(2, 2), z=-1)
    Text('SELECT LEVEL', parent=state.level_select_panel,
         y=0.36, scale=2.5, color=color.orange, origin=(0, 0))

    for idx, lvl in enumerate(LEVELS):
        lid  = lvl['id']
        pb   = state.pbs.get(lid)
        goal = lvl.get('baseline_time')
        row_y = 0.18 - idx * 0.13

        def _make_play(level_id):
            def _play():
                from game import start_game
                _destroy(state.level_select_panel)
                state.level_select_panel = None
                start_game(level_id)
            return _play

        # Level name as a clickable button (centred, y-only positioning)
        Button(f'{lid}.  {lvl["name"]}', parent=state.level_select_panel,
               scale=(0.50, 0.08), y=row_y + 0.03, on_click=_make_play(lid))
        # Goal / PB info line directly below the button
        Text(f'GOAL {_fmt(goal)}     PB {_fmt(pb)}',
             parent=state.level_select_panel,
             y=row_y - 0.04, scale=0.75, color=color.white, origin=(0, 0))

    def _back():
        _destroy(state.level_select_panel)
        state.level_select_panel = None
        show_main_menu()

    Button('Back', parent=state.level_select_panel,
           scale=(0.25, 0.09), y=-0.44, on_click=_back)


# ── Settings ───────────────────────────────────────────────────────────────
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
    Button('1280x720 Windowed', parent=state.settings_panel, scale=(0.38, 0.09), y=-0.05,
           on_click=lambda: (setattr(window, 'fullscreen', False),
                             setattr(window, 'size', Vec2(1280, 720))))

    Text('Audio', parent=state.settings_panel, y=-0.17, scale=1.1,
         color=color.light_gray, origin=(0, 0))
    Slider(min=0, max=1, default=0.7, text='Music', parent=state.settings_panel,
           position=(-0.22, -0.31), scale=0.55)
    Slider(min=0, max=1, default=1.0, text='SFX', parent=state.settings_panel,
           position=(-0.22, -0.41), scale=0.55)

    def _back():
        _destroy(state.settings_panel); state.settings_panel = None
        if back_fn:
            back_fn()

    Button('Back', parent=state.settings_panel, scale=(0.3, 0.09), y=-0.54, on_click=_back)


# ── Pause ──────────────────────────────────────────────────────────────────
def show_pause():
    state.paused = True
    _destroy(state.pause_panel)
    state.pause_panel = Entity(parent=camera.ui, model='quad',
                               color=color.rgba(0, 0, 0, 180), scale=(0.72, 0.72), z=-1)
    Text('PAUSED', parent=state.pause_panel, y=0.28, scale=2.5, origin=(0, 0))

    def _resume():
        state.paused = False
        _destroy(state.pause_panel); state.pause_panel = None

    def _restart():
        from game import restart_level
        state.paused = False
        _destroy(state.pause_panel); state.pause_panel = None
        restart_level()

    def _to_menu():
        state.paused = False
        _destroy(state.pause_panel); state.pause_panel = None
        show_main_menu()

    Button('Resume',    parent=state.pause_panel, scale=(0.33, 0.1), y=0.10, on_click=_resume)
    Button('Restart',   parent=state.pause_panel, scale=(0.33, 0.1), y=-0.04, on_click=_restart)
    Button('Settings',  parent=state.pause_panel, scale=(0.33, 0.1), y=-0.18,
           on_click=lambda: show_settings(back_fn=show_pause))
    Button('Main Menu', parent=state.pause_panel, scale=(0.33, 0.1), y=-0.32, on_click=_to_menu)


# ── Death screen ───────────────────────────────────────────────────────────
def show_death_screen():
    from level_data import LEVELS
    _destroy(state.death_panel)
    state.death_panel = Entity(parent=camera.ui, model='quad',
                               color=color.rgba(0, 0, 0, 210), scale=(0.75, 0.60), z=-1)
    lvl      = LEVELS[state.current_level - 1]
    lvl_name = lvl['name']
    goal     = lvl.get('baseline_time')

    Text('DEAD', parent=state.death_panel, y=0.22, scale=3.5, color=color.red, origin=(0, 0))
    Text(lvl_name, parent=state.death_panel, y=0.06, scale=1.2, color=color.orange, origin=(0, 0))
    Text(f'Time: {_fmt(state.level_timer)}', parent=state.death_panel,
         y=-0.05, scale=1.3, color=color.white, origin=(0, 0))

    if goal is not None:
        delta = state.level_timer - goal
        sign  = '+' if delta >= 0 else ''
        col   = color.lime if delta < 0 else color.red
        Text(f'Goal: {_fmt(goal)}  ({sign}{delta:.2f}s)',
             parent=state.death_panel, y=-0.16, scale=0.9, color=col, origin=(0, 0))

    def _restart():
        from game import restart_level
        _destroy(state.death_panel); state.death_panel = None
        restart_level()

    def _menu():
        _destroy(state.death_panel); state.death_panel = None
        show_main_menu()

    Button('Restart',   parent=state.death_panel, scale=(0.3, 0.1), y=-0.28, on_click=_restart)
    Button('Main Menu', parent=state.death_panel, scale=(0.3, 0.1), y=-0.41, on_click=_menu)


# ── Level complete ─────────────────────────────────────────────────────────
def show_level_complete(run_time, pb_time, is_new_pb, level_id):
    from level_data import LEVELS
    _destroy(state.level_complete_panel)
    state.level_complete_panel = Entity(parent=camera.ui, model='quad',
                                        color=color.rgba(0, 0, 0, 215),
                                        scale=(0.82, 0.76), z=-1)
    lvl      = LEVELS[level_id - 1]
    lvl_name = lvl['name']
    goal     = lvl.get('baseline_time')

    Text('LEVEL CLEAR', parent=state.level_complete_panel,
         y=0.30, scale=2.8, color=color.gold, origin=(0, 0))
    Text(lvl_name, parent=state.level_complete_panel,
         y=0.17, scale=1.2, color=color.orange, origin=(0, 0))

    Text('TIME', parent=state.level_complete_panel,
         y=0.06, scale=0.9, color=color.light_gray, origin=(0, 0))
    Text(_fmt(run_time), parent=state.level_complete_panel,
         y=-0.02, scale=2.0, color=color.white, origin=(0, 0))

    if goal is not None:
        delta = run_time - goal
        sign  = '+' if delta >= 0 else ''
        col   = color.lime if delta < 0 else color.red
        tag   = 'GOAL BEATEN!' if delta < 0 else 'goal missed'
        Text(f'Goal: {_fmt(goal)}   {sign}{delta:.2f}s  {tag}',
             parent=state.level_complete_panel, y=-0.12, scale=0.82, color=col, origin=(0, 0))

    if is_new_pb:
        Text('NEW RECORD!', parent=state.level_complete_panel,
             y=-0.21, scale=1.6, color=color.yellow, origin=(0, 0))
    else:
        Text(f'PB  {_fmt(pb_time)}', parent=state.level_complete_panel,
             y=-0.21, scale=1.1, color=color.cyan, origin=(0, 0))

    has_next = level_id < len(LEVELS)

    def _next():
        from game import start_game
        _destroy(state.level_complete_panel); state.level_complete_panel = None
        start_game(level_id + 1)

    def _retry():
        from game import restart_level
        _destroy(state.level_complete_panel); state.level_complete_panel = None
        restart_level()

    def _menu():
        _destroy(state.level_complete_panel); state.level_complete_panel = None
        show_main_menu()

    btn_y = -0.33
    if has_next:
        Button('Next Level', parent=state.level_complete_panel,
               scale=(0.30, 0.10), position=(-0.18, btn_y), on_click=_next)
        Button('Retry',      parent=state.level_complete_panel,
               scale=(0.20, 0.10), position=( 0.17, btn_y), on_click=_retry)
    else:
        Text('YOU WIN!', parent=state.level_complete_panel,
             y=btn_y + 0.05, scale=1.8, color=color.gold, origin=(0, 0))
        Button('Retry',     parent=state.level_complete_panel,
               scale=(0.25, 0.10), position=(-0.14, btn_y - 0.08), on_click=_retry)
        Button('Main Menu', parent=state.level_complete_panel,
               scale=(0.25, 0.10), position=( 0.14, btn_y - 0.08), on_click=_menu)
        return

    Button('Menu', parent=state.level_complete_panel,
           scale=(0.18, 0.10), position=(0.36, btn_y), on_click=_menu)
