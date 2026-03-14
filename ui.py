"""
All UI: HUD, main menu, level select, settings, pause, death, level complete.

Windows fix: Text entities must be parented to camera.ui directly —
             parenting to a non-camera.ui entity silently hides them on Windows.
             Each screen is stored as a list of entities; _close() destroys them all.
"""
from ursina import *
import state
from state import _destroy


# ── Helpers ────────────────────────────────────────────────────────────────
def _fmt(t):
    if t is None:
        return '--:--.--'
    mins = int(t) // 60
    secs = t % 60
    return f'{mins}:{secs:05.2f}' if mins > 0 else f'{secs:.2f}'


def _close(panel_attr):
    """Destroy all entities in a screen list and clear the state attr."""
    lst = getattr(state, panel_attr, None)
    if isinstance(lst, list):
        for e in lst:
            try:
                destroy(e)   # call Ursina destroy directly — bypasses the
            except Exception:   # `if ent:` guard in state._destroy which
                pass             # returns False when enabled=False
    elif lst is not None:
        try:
            destroy(lst)
        except Exception:
            pass
    setattr(state, panel_attr, None)


def _panel(elems, w=2, h=2, alpha=200):
    """Add a full- or partial-screen black backdrop to the entity list.
    z=0.1 puts it BEHIND text/buttons which sit at the default z=0."""
    elems.append(Entity(parent=camera.ui, model='quad',
                        color=color.rgba(0, 0, 0, alpha),
                        scale=(w, h), z=0.1))


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
    _close('menu_panel')
    elems = []
    state.menu_panel = elems

    _panel(elems)
    elems.append(Text('SPAGHETTI BANDIT', parent=camera.ui,
                       y=0.36, scale=3, color=color.orange, origin=(0, 0)))
    elems.append(Text('A/D – Move   |   S – Duck   |   Space – Jump',
                       parent=camera.ui, y=0.22, scale=0.85,
                       color=color.gray, origin=(0, 0)))
    elems.append(Text('Shift – Grapple   |   F – Parry',
                       parent=camera.ui, y=0.14, scale=0.85,
                       color=color.gray, origin=(0, 0)))

    def _levels():
        _close('menu_panel')
        show_level_select()

    def _settings():
        _close('menu_panel')
        show_settings(back_fn=show_main_menu)

    elems.append(Button('Play',     parent=camera.ui, scale=(0.25, 0.1), y=0.00,  on_click=_levels))
    elems.append(Button('Settings', parent=camera.ui, scale=(0.25, 0.1), y=-0.14, on_click=_settings))
    elems.append(Button('Quit',     parent=camera.ui, scale=(0.25, 0.1), y=-0.28, on_click=application.quit))


# ── Level select ───────────────────────────────────────────────────────────
def show_level_select():
    from level_data import LEVELS
    _close('level_select_panel')
    elems = []
    state.level_select_panel = elems

    _panel(elems)
    elems.append(Text('SELECT LEVEL', parent=camera.ui,
                       y=0.40, scale=2.5, color=color.orange, origin=(0, 0)))

    cols    = 3
    col_xs  = [-0.38, 0.00, 0.38]
    row_ys  = [0.16, -0.14]   # y centre for each row of cards

    for idx, lvl in enumerate(LEVELS):
        lid  = lvl['id']
        pb   = state.pbs.get(lid)
        goal = lvl.get('baseline_time')
        col  = idx % cols
        row  = idx // cols
        cx   = col_xs[col]
        cy   = row_ys[row] if row < len(row_ys) else row_ys[-1] - (row - len(row_ys) + 1) * 0.30

        def _make_play(level_id):
            def _play():
                from game import start_game
                _close('level_select_panel')
                start_game(level_id)
            return _play

        elems.append(Button(f'{lid}. {lvl["name"]}', parent=camera.ui,
                             scale=(0.28, 0.09), position=(cx, cy + 0.02),
                             on_click=_make_play(lid)))
        elems.append(Text(f'GOAL {_fmt(goal)}', parent=camera.ui,
                           position=(cx, cy - 0.07), scale=0.70,
                           color=color.yellow, origin=(0, 0)))
        elems.append(Text(f'PB  {_fmt(pb)}', parent=camera.ui,
                           position=(cx, cy - 0.13), scale=0.70,
                           color=color.cyan, origin=(0, 0)))

    def _back():
        _close('level_select_panel')
        show_main_menu()

    elems.append(Button('Back', parent=camera.ui,
                         scale=(0.25, 0.09), y=-0.42, on_click=_back))


# ── Settings ───────────────────────────────────────────────────────────────
def show_settings(back_fn=None):
    _close('settings_panel')
    elems = []
    state.settings_panel = elems

    _panel(elems, w=0.95, h=0.95, alpha=230)
    elems.append(Text('Settings', parent=camera.ui,
                       y=0.40, scale=2.2, origin=(0, 0)))

    elems.append(Text('Display', parent=camera.ui,
                       y=0.28, scale=1.1, color=color.light_gray, origin=(0, 0)))
    elems.append(Button('Fullscreen', parent=camera.ui, scale=(0.38, 0.09), y=0.17,
                         on_click=lambda: setattr(window, 'fullscreen', True)))
    elems.append(Button('Borderless Fullscreen', parent=camera.ui, scale=(0.38, 0.09), y=0.06,
                         on_click=lambda: setattr(window, 'borderless', True)))
    elems.append(Button('1280x720 Windowed', parent=camera.ui, scale=(0.38, 0.09), y=-0.05,
                         on_click=lambda: setattr(window, 'size', Vec2(1280, 720))))

    elems.append(Text('Audio', parent=camera.ui,
                       y=-0.17, scale=1.1, color=color.light_gray, origin=(0, 0)))

    def _back():
        _close('settings_panel')
        if back_fn:
            back_fn()

    elems.append(Button('Back', parent=camera.ui,
                         scale=(0.3, 0.09), y=-0.35, on_click=_back))


# ── Pause ──────────────────────────────────────────────────────────────────
def show_pause():
    state.paused = True
    _close('pause_panel')
    elems = []
    state.pause_panel = elems

    _panel(elems, w=0.72, h=0.72, alpha=180)
    elems.append(Text('PAUSED', parent=camera.ui,
                       y=0.28, scale=2.5, origin=(0, 0)))

    def _resume():
        state.paused = False
        _close('pause_panel')

    def _restart():
        from game import restart_level
        state.paused = False
        _close('pause_panel')
        restart_level()

    def _to_menu():
        state.paused = False
        _close('pause_panel')
        show_main_menu()

    elems.append(Button('Resume',    parent=camera.ui, scale=(0.33, 0.1), y=0.10,  on_click=_resume))
    elems.append(Button('Restart',   parent=camera.ui, scale=(0.33, 0.1), y=-0.04, on_click=_restart))
    elems.append(Button('Settings',  parent=camera.ui, scale=(0.33, 0.1), y=-0.18,
                         on_click=lambda: show_settings(back_fn=show_pause)))
    elems.append(Button('Main Menu', parent=camera.ui, scale=(0.33, 0.1), y=-0.32, on_click=_to_menu))


# ── Death screen ───────────────────────────────────────────────────────────
def show_death_screen():
    from level_data import LEVELS
    _close('death_panel')
    elems = []
    state.death_panel = elems

    _panel(elems, w=0.75, h=0.60, alpha=210)
    lvl  = LEVELS[state.current_level - 1]
    goal = lvl.get('baseline_time')

    elems.append(Text('DEAD', parent=camera.ui,
                       y=0.22, scale=3.5, color=color.red, origin=(0, 0)))
    elems.append(Text(lvl['name'], parent=camera.ui,
                       y=0.08, scale=1.2, color=color.orange, origin=(0, 0)))
    elems.append(Text(f'Time: {_fmt(state.level_timer)}', parent=camera.ui,
                       y=-0.03, scale=1.3, color=color.white, origin=(0, 0)))

    if goal is not None:
        delta = state.level_timer - goal
        sign  = '+' if delta >= 0 else ''
        col   = color.lime if delta < 0 else color.red
        elems.append(Text(f'Goal: {_fmt(goal)}  ({sign}{delta:.2f}s)',
                           parent=camera.ui, y=-0.14, scale=0.9,
                           color=col, origin=(0, 0)))

    def _restart():
        from game import restart_level
        _close('death_panel')
        restart_level()

    def _menu():
        _close('death_panel')
        show_main_menu()

    elems.append(Button('Restart',   parent=camera.ui, scale=(0.3, 0.1), y=-0.26, on_click=_restart))
    elems.append(Button('Main Menu', parent=camera.ui, scale=(0.3, 0.1), y=-0.39, on_click=_menu))


# ── Level complete ─────────────────────────────────────────────────────────
def show_level_complete(run_time, pb_time, is_new_pb, level_id):
    from level_data import LEVELS
    _close('level_complete_panel')
    elems = []
    state.level_complete_panel = elems

    _panel(elems, w=0.82, h=0.76, alpha=215)
    lvl  = LEVELS[level_id - 1]
    goal = lvl.get('baseline_time')

    elems.append(Text('LEVEL CLEAR', parent=camera.ui,
                       y=0.30, scale=2.8, color=color.gold, origin=(0, 0)))
    elems.append(Text(lvl['name'], parent=camera.ui,
                       y=0.18, scale=1.2, color=color.orange, origin=(0, 0)))
    elems.append(Text('TIME', parent=camera.ui,
                       y=0.07, scale=0.9, color=color.light_gray, origin=(0, 0)))
    elems.append(Text(_fmt(run_time), parent=camera.ui,
                       y=-0.01, scale=2.0, color=color.white, origin=(0, 0)))

    if goal is not None:
        delta = run_time - goal
        sign  = '+' if delta >= 0 else ''
        col   = color.lime if delta < 0 else color.red
        tag   = 'GOAL BEATEN!' if delta < 0 else 'goal missed'
        elems.append(Text(f'Goal: {_fmt(goal)}   {sign}{delta:.2f}s  {tag}',
                           parent=camera.ui, y=-0.12, scale=0.82,
                           color=col, origin=(0, 0)))

    if is_new_pb:
        elems.append(Text('NEW RECORD!', parent=camera.ui,
                           y=-0.21, scale=1.6, color=color.yellow, origin=(0, 0)))
    else:
        elems.append(Text(f'PB  {_fmt(pb_time)}', parent=camera.ui,
                           y=-0.21, scale=1.1, color=color.cyan, origin=(0, 0)))

    has_next = level_id < len(LEVELS)

    def _next():
        from game import start_game
        _close('level_complete_panel')
        start_game(level_id + 1)

    def _retry():
        from game import restart_level
        _close('level_complete_panel')
        restart_level()

    def _menu():
        _close('level_complete_panel')
        show_main_menu()

    if has_next:
        elems.append(Button('Next Level', parent=camera.ui,
                             scale=(0.30, 0.10), position=(-0.18, -0.33), on_click=_next))
        elems.append(Button('Retry',      parent=camera.ui,
                             scale=(0.20, 0.10), position=( 0.08, -0.33), on_click=_retry))
        elems.append(Button('Menu',       parent=camera.ui,
                             scale=(0.18, 0.10), position=( 0.28, -0.33), on_click=_menu))
    else:
        elems.append(Text('YOU WIN!', parent=camera.ui,
                           y=-0.28, scale=1.8, color=color.gold, origin=(0, 0)))
        elems.append(Button('Retry',     parent=camera.ui,
                             scale=(0.25, 0.10), position=(-0.14, -0.40), on_click=_retry))
        elems.append(Button('Main Menu', parent=camera.ui,
                             scale=(0.25, 0.10), position=( 0.14, -0.40), on_click=_menu))
