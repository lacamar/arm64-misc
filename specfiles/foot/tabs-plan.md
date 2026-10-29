# foot vertical tabs — implementation plan

Status: draft r11 · Target: foot 1.28.0-11 (arm64-misc downstream) · Patch: `foot-tabs.patch` (Patch2)

## 1. Goal

A foot window can hold several terminals ("tabs"). When a window has two or more tabs, a vertical
sidebar on its left lists them, as in Zen browser's vertical tabs. Clicking a title switches to that
tab; a `+` row opens a new one; rows drag to reorder, and dragging one out detaches it into its own
window. A window holds one or more named **workspaces** (e.g. `CBC`, `general`), each with its own
tab list; a switcher row at the bottom of the sidebar switches between them, a double-click renames
one in place, and `footclient --workspace` / `foot --tab` target them. Two or more tabs can be shown
side by side as a **split** that takes one sidebar row. Inactive tabs show a marker for bell and for
new output. Tabs, splits, workspaces and the active tab survive the existing downstream session
restore.

### Why in foot, not the compositor

niri's tabbed columns already group windows, but show only indicator bars, no titles and no named
groups. tmux/zellij add a second terminal-state layer (scrollback, keybindings, graphics protocols)
on top of foot. Doing it in foot keeps one renderer, real scrollback and sixel, and lets session
restore save the group as one unit.

### Non-goals

- Vertical splits, nested splits, per-pane resize ratio (equal widths only).
- Dragging a row into a pane to join a split; dragging across workspaces other than dropping on a
  switcher chip.
- `wl_data_device` DnD for tabs (drag is pointer-grab based, one process).
- Placing a detached window (xdg-shell cannot position toplevels).
- `foot --tab` finding a workspace that only exists in a non-focused foot process (§7.3).
- Wheel scrolling of the tab list.

## 2. Decisions

| # | Decision | Why |
|---|----------|-----|
| D1 | `struct wl_window` is shared by its tabs. `win->term` stays and means **focused tab** (focused pane when split). New `tll(struct terminal *) tabs`. Every `term->window` keeps pointing at its window. | All input already resolves surface → `win` → `win->term` (`input.c:702-721`, `:2477-2481`, `ime.c:59-70`). Keeping that field as "active" makes keyboard, pointer, touch and IME follow the active tab with no changes. The ~190 `term->window` uses stay valid. |
| D2 | Hidden tabs keep running: PTY reads, VT parsing, grid updates, TIOCSWINSZ. They never render or commit. | Programs in background tabs must not stall. Gating at render time is one check in two places (§5.1). |
| D3 | Grid buffer chains, `last_buf`, damage state stay **per terminal**. On switch, `last_buf` is dropped so the new tab does a full repaint. | Moving chains to the window would touch every render path. A full repaint per switch is cheap (Vulkan already repaints every frame, `render.c:3412`). |
| D4 | The sidebar is a new subsurface **inside** the main surface at x=0, over a left margin added to the terminal's padding. The window's size does not change when the sidebar appears; the grid gets narrower. | Works under both CSD and SSD (niri) with no window-geometry changes. Mouse→cell mapping, selection and margins already honour `margins.left`. Rejected: placing the sidebar outside the surface at negative x like CSD borders — more geometry code and compositor clipping risk. |
| D5 | Sidebar text uses the active tab's primary font (`term->fonts[0]`); colours come from the active tab's palette. Font-size bindings apply to **all tabs** of a window. | Already loaded at the right scale and DPI; zero new config. Window-wide font size: tabs share one surface size, and per-tab cell sizes would make `resize_by_cells` snap each tab to a different `term->width`. |
| D6 | `[main] workspace=` = the workspace a new instance lands in: the first workspace's name for a new window, the target workspace for `--tab`. `--workspace=NAME` on foot/footclient is sugar for `-o workspace=NAME`; footclient's `--workspace` on the command line also sets the tab bit (§7.4). | Overrides already travel over the client protocol (`client.c:209-330`). Client-side tab bit, so a `workspace=` in foot.ini does not turn every plain footclient into a tab. |
| D7 | `footclient --tab` uses one of the 5 reserved bits in `struct client_data` (`client-protocol.h:12-31`). | Struct size and the `_Static_assert` stay the same. An old server ignores the bit and opens a window, which is the right fallback. |
| D8 | Creating a tab goes through a `tab_host` callback set on `struct wayland` by whoever owns terminal lifetimes (main.c standalone, server.c server mode). | Standalone and server mode manage terminals differently (shutdown callback vs `terminal_instance`, `server.c:62-68`). The keybinding, sidebar `+` and merge code call one function and don't care which. |
| D9 | Session-state format v5 (current is v4, `session.c:28`). v2–v4 files load as one-tab windows. | Grouping must be stored per window; the xdg toplevel_session id is per window (`wayland.h:387`). |
| D10 | Tabs ship as a separate `foot-tabs.patch` applied after `foot-session-restore.patch` and `foot-vulkan.patch`. | Reviewable and droppable on its own. Cost: regenerating the session patch forces a rebase; that patch is stable (last change 2026-10-07). |
| D11 | Numbered actions (`select-tab-N`, `select-workspace-N`, `move-tab-to-workspace-N`) are 9 separate actions each. | Avoids a new aux-argument parser; table entries are trivial. |
| D12 | Window title = `NAME: <tab title>`, NAME = current workspace's name; no prefix while unnamed. | Workspace stays visible when the sidebar is hidden and in the compositor's window list. |
| D13 | A window holds 1..N workspaces, each with a name (NULL = unnamed, shown as its 1-based index), its own active tab, and ≥1 tab; a workspace whose last tab leaves is dropped. `win->tabs` keeps **all** tabs in display order; each tab points at its workspace (`term->ws`); the sidebar shows only `win->ws`'s tabs. | ≥1 tab per workspace means "2+ workspaces" implies "2+ tabs", so the sidebar threshold counts all tabs unchanged. Resize/scale/font/close/merge/session loops over `win->tabs` stay as they are and every tab is sized to the window, so switching workspace never resizes. |
| D14 | Workspace names are unique per window; two windows may share one. | `--workspace` targeting and merge-by-name need a unique match inside a window. |
| D15 | Inline rename is a window-level line editor that takes keyboard input ahead of the pty; hardcoded keys, no actions; IME commit-string only. | Same dispatch shape as `unicode_mode`/`is_searching` (`input.c:1648-1663`). Search's action-driven editor (`search.c:1218-1260`) is more than rename needs. |
| D16 | Split view: a group of adjacent tabs (same workspace) shown side by side, each in its own desync subsurface; `win->term` = focused pane. | Keeps D1 and D3: each pane commits its own surface. Rejected: compositing panes into one buffer — `grid_render` attaches and commits itself and damage is per term. |
| D17 | Merge and detach share one per-tab move, `tabs_transfer` (§5.9). Drag is a pointer grab on the sidebar subsurface, not `wl_data_device`. | One code path for "tab changes window". DnD would need a data source, mime type and a drop on our own window for a one-process move. |
| D18 | Standalone `foot --tab`: every foot with a socket repoints one symlink in `$XDG_RUNTIME_DIR` at itself on focus; `foot --tab` connects through it and execs footclient. | Reuses the server path for serving and footclient for sending; no new protocol. |
| D19 | Activity marker: output read while a tab is hidden, except within 500 ms after foot itself provoked it (resize, theme report, focus-out report). | SIGWINCH/focus redraws are the known false positives; muting at their source is cheaper than diffing content. |

## 3. User-facing behaviour

### 3.1 Sidebar

```
┌──────────────┬──────────────────────┐
│▌nvim plan.md │ ~/src/cbc $ make     │
│  make │ htop │                      │
│• ssh prod    │                      │
│◦ tail -f log │                      │
│ +            │                      │
│──────────────│                      │
│[CBC] gen  3• │                      │
└──────────────┴──────────────────────┘
```

- Visible when the window has ≥2 tabs in total (D13). Hidden with one tab (looks like plain foot).
- Tab rows: only the tabs of the current workspace. One row per tab, or per split group with label
  `title1 │ title2 …`. Title = `term->window_title` (fallback `foot`), truncated with `…`. Active row
  (the visible tab/group) highlighted with a 3px accent bar.
- Markers on hidden tabs: `•` bell since last active (§5.6), `◦` output since last active (§5.14);
  bell wins. A group row shows a marker if any hidden member has one.
- `+` row directly below the last tab row.
- Switcher row pinned to the bottom, 1px separator above, shown when the window has ≥2 workspaces or
  the current one is named. Chips left to right, each `width / count` wide, holding the name (or
  index) truncated with `…`; current chip in active-row colours; `•`/`◦` after a chip = OR of its
  tabs' markers. During a rename the current chip is the edit field (§5.12).
- Width: `[tabs] width=` logical pixels, default 200. Row height = font line height + 2×4px.
- More rows than fit above the switcher: the list scrolls so the active row stays visible.

### 3.2 Mouse

- Left press on a tab row: switch to it. Dragging past half a row reorders live (group = one block);
  releasing outside the sidebar detaches the row (whole group) into a new window; releasing over a
  switcher chip moves the row to that workspace (§6.7).
- Middle click on a tab row: close that tab (group row: the focused member if visible, else first).
- Left click on `+`: new tab (cwd of the active tab).
- Left click on a chip: switch workspace. Double-click (`seat->mouse.count == 2`, counted at
  `input.c:2990-2997`): switch, then rename (§5.12). Middle click on a chip: nothing.
- Click on an unfocused pane: focuses it; the click also lands (§5.13).
- Pointer over sidebar: default arrow; `grabbing` while dragging.

### 3.3 Key actions (`[key-bindings]`)

| Action | Default | Effect |
|---|---|---|
| `new-tab` | `Control+Shift+t` | New tab in the current workspace, cwd = active tab's live cwd |
| `next-tab` / `prev-tab` | `Control+Shift+Next` / `Control+Shift+Prior` | Cycle rows of the current workspace, wrapping (group = one step, lands on its first member) |
| `move-tab-down` / `move-tab-up` | none | Reorder active row (group moves as a block) |
| `select-tab-1`…`select-tab-9` | none | Jump to row N; `-9` = last row |
| `close-tab` | none | `term_shutdown` on the focused tab/pane (`quit` closes the whole window) |
| `merge-window` | none | Move all tabs into the most recently focused other window, then close this one |
| `detach-tab` | none | Move the focused tab (pane alone if split) into a new window; no-op with one tab |
| `new-workspace` | none | New unnamed workspace at the end with one new tab (cwd of active tab); switch to it |
| `next-workspace` / `prev-workspace` | none | Cycle, wrapping |
| `select-workspace-1`…`-9` | none | Jump; `-9` = last |
| `move-tab-to-workspace-1`…`-9` | none | Move active row to workspace N (appended); N = count+1 creates an unnamed one; larger ignored; emptied source dropped; follow the tab |
| `rename-workspace` | none | Rename the current workspace in place (§5.12) |
| `split-new` | none | New tab right of the focused pane in its group (creates the group); focus moves to it |
| `split-next` | none | The row after the focused group joins it; no-op if none |
| `unsplit` | none | Dissolve the focused group into adjacent rows; focused stays active |
| `focus-pane-next` / `focus-pane-prev` | none | Cycle focus within the group, wrapping |

`Control+Shift+t` and `Control+Shift+Prior/Next` are not default-bound today (checked
`add_default_key_bindings` in `config.c`). `Control+Prior/Next` stay unbound: tmux/vim/irssi use
them. foot's free Control+Shift chords are scarce, so the rest ship unbound with commented examples
in `foot.ini`.

`quit` (`input.c:456`), CSD close button (`input.c:3244`) and compositor close
(`xdg_toplevel_close`, `wayland.c:971`) close **all** tabs of the window, every workspace.

### 3.4 Command line

- `footclient --tab`: tab in the current workspace of the most recently focused window; else a new
  window.
- `footclient --workspace=NAME` (implies `--tab`): the window that has NAME (highest `focus_seq`
  among matches) → tab appended to NAME, which becomes current. No window has it → NAME is created
  at the end of the most recently focused window. No window → new window whose first workspace is
  NAME.
- `foot --workspace=NAME`: name of the new window's first workspace.
- `foot --tab`: same targeting as `footclient --tab`, over every foot process of this user on this
  Wayland display (servers and standalone, §7.3). None reachable → opens as a new standalone window.
  Rejected with `--server` or `--pty` (pattern `main.c:439`), exit 1.
- `-o workspace=NAME` works as a config override.

### 3.5 Config

```ini
[main]
workspace=          # workspace for new windows / --tab target; default empty

[tabs]
width=200           # logical px
activity=yes        # mark hidden tabs that print output
```

## 4. Data model

`wayland.h`:

```c
struct tab_ws {
    char *name;                       /* NULL = unnamed; owned; unique per window */
    struct terminal *active;          /* last active tab of this workspace */
};
```

`struct wl_window`:

```c
struct terminal *term;              /* focused tab/pane (unchanged name) */
tll(struct terminal *) tabs;        /* all workspaces, display order */
tll(struct tab_ws *) workspaces;    /* switcher order; never empty while tabs exist */
struct tab_ws *ws;                  /* current; win->term->ws == win->ws */
struct {
    struct tab_ws *ws;              /* NULL = not renaming */
    char32_t *buf;
    size_t len, sz, cursor;
} rename;
struct wayl_sub_surface sidebar;    /* created on demand, pointer input enabled */
struct buffer_chain *sidebar_chain; /* shm, owned by window */
struct buffer_chain *bg_chain;      /* split background, §5.13 */
int layout_w, layout_h;             /* logical, last tabs_layout */
uint64_t focus_seq;                 /* wayl->focus_counter at last keyboard enter */
int sidebar_scroll;                 /* first visible row */
bool sidebar_dirty;
bool closing;                       /* whole-window close in progress, §5.5 */
bool adopted;                       /* holds a moved tab: first configure skips term_window_configured, §5.10 */
struct {
    struct seat *seat;
    struct terminal *tab;           /* NULL = no press armed */
    int start_y;                    /* buffer px */
    bool dragging;
    bool out;                       /* outside the sidebar: release detaches */
} sidebar_drag;
```

No cached logical size for unsplit tabs: `render_resize` snaps/clamps its input and output changes
resize without a configure, so a cached value goes stale. Relayout derives it from the active tab
(`win->term->width / win->term->scale`, as `update_term_for_output_change` does, `wayland.c:417`).
Split windows use `layout_w/h` (§5.13): `RESIZE_PANE` never snaps and scale changes keep logical size.

`struct wayland`:

```c
uint64_t focus_counter;
uint32_t group_counter;             /* split ids, unique across windows */
tll(struct wl_window *) windows;    /* none exists in 1.28; pushed in wayl_win_init,
                                       removed at the top of wayl_win_destroy */
char *tab_sock_path;                /* own socket, set by server_init; §7.3 */
bool tab_sock_owner;                /* pointer symlink currently ours */
struct {
    bool (*new_tab)(void *data, struct wl_window *win, struct tab_ws *ws, bool split,
                    const char *cwd, int argc, char *const *argv);
    void (*window_closing)(void *data, struct wl_window *win);              /* NULL standalone */
    void (*tab_moved)(void *data, struct terminal *term, struct wl_window *dst); /* NULL standalone */
    void *data;
} tab_host;
```

`terminal.h`, `struct terminal`:

```c
struct tab_ws *ws;
bool tab_marker;                 /* bell while hidden; cleared when shown */
bool tab_activity;               /* output while hidden; cleared when shown */
bool tab_shown;                  /* shown at least once; gates tab_activity */
uint64_t activity_mute_until;    /* CLOCK_MONOTONIC ms */
uint32_t group;                  /* split id, 0 = none */
struct wayl_sub_surface pane;    /* only while its group is visible */
struct wl_callback *pane_cb;
```

`enum term_surface` (`terminal.h:354`): add `TERM_SURF_SIDEBAR`.

Helpers (new `tabs.c` / `tabs.h`):

```c
bool tabs_is_active(const struct terminal *term);          /* window && term == window->term */
bool tabs_is_visible(const struct terminal *term);         /* active, or in the active group */
bool tabs_sidebar_visible(const struct wl_window *win);    /* tll_length(win->tabs) >= 2 */
int  tabs_sidebar_width_px(const struct wl_window *win);   /* roundf(width * win->term->scale), 0 below 2 tabs */
void tabs_activate(struct wl_window *win, struct terminal *term);
void tabs_attach(struct wl_window *win, struct terminal *term, struct terminal *after,
                 struct tab_ws *ws, bool split);
void tabs_detach(struct terminal *term);                    /* unlink on close or move */
void tabs_move(struct wl_window *win, int delta);           /* active row, within win->ws */
void tabs_select_index(struct wl_window *win, int idx);     /* row in win->ws; -1 = last */
bool tabs_new(struct terminal *from, struct tab_ws *ws, bool split);  /* calls tab_host.new_tab */
void tabs_transfer(struct terminal *t, struct wl_window *dst, struct tab_ws *dst_ws, bool keep_focus);
bool tabs_merge_into(struct wl_window *src, struct wl_window *dst);
bool tabs_detach_window(struct terminal *t, bool whole_group);
struct wl_window *tabs_find_target(struct wayland *wayl, const char *ws, struct tab_ws **out);
void tabs_layout(struct wl_window *win, int w, int h);      /* resize all tabs; panes; sidebar show/hide */
void tabs_relayout(struct wl_window *win);                  /* tabs_layout(win, tabs_win_size(...)) */
void tabs_win_size(const struct wl_window *win, int *w, int *h);
void tabs_close_window(struct wl_window *win);              /* closing = true; term_shutdown all */
struct tab_ws *tabs_ws_find(struct wl_window *win, const char *name);  /* NULL never matches */
struct tab_ws *tabs_ws_add(struct wl_window *win, const char *name);   /* append */
void tabs_ws_set(struct terminal *term, struct tab_ws *ws);             /* move row, drop emptied ws */
void tabs_select_ws(struct wl_window *win, struct tab_ws *ws);
void tabs_select_ws_index(struct wl_window *win, int idx);              /* -1 = last */
void tabs_cycle_ws(struct wl_window *win, int delta);
int  tabs_row_count(const struct wl_window *win);           /* rows of win->ws */
struct terminal *tabs_row_term(const struct wl_window *win, int row);   /* first member */
size_t tabs_group_len(const struct terminal *t);
void tabs_focus_pane(struct wl_window *win, struct terminal *t);
struct terminal *tabs_term_for_surface(struct wl_window *win, struct wl_surface *s);
bool tabs_split_new(struct terminal *from);
bool tabs_split_next(struct wl_window *win);
void tabs_unsplit(struct wl_window *win);
void rename_begin(struct wl_window *win, struct tab_ws *ws);
void rename_cancel(struct wl_window *win);
void rename_input(struct seat *seat, struct wl_window *win, xkb_keycode_t key, xkb_keysym_t sym,
                  xkb_mod_mask_t mods, xkb_mod_mask_t consumed);
void rename_add_utf8(struct wl_window *win, const char *s, size_t len);
```

`render.h`: `RESIZE_PANE = 1 << 3`, `term_surf(term)`, `term_frame_cb(term)`, `term_pane_x(term)`.

Sidebar drawing lives in `render.c` next to `render_csd` (`render_sidebar`), because it uses the
static `render_osd`-style text helpers there.

## 5. Core mechanics

### 5.1 Render gating

Hidden tabs must not commit. Add `if (!tabs_is_visible(term)) continue;` / `return` at items 1–3, 7;
items 4–6, 8 are window-level and use `tabs_is_active`. Without a split both are the same test.

`grid_render` has exactly two callers (`render.c:4403` in `frame_callback`, `:5243` in the hook),
so gating 1–2 plus `xassert(tabs_is_visible(term))` in `grid_render` covers the main commit path.

1. Top of the loop body in `fdm_hook_refresh_pending_terminals` (`render.c:5204`). Do **not** clear
   the term's `refresh.*` flags; they're picked up when shown.
2. `frame_callback` (`render.c:4366`): it is armed with `data = term` (`render.c:3730`). Once tabs
   exist the window outlives a closed tab, so a callback in flight would dereference a freed term
   (UAF). Register `win` as data and use `win->term` inside; this also makes a callback armed by the
   previous tab render the new one. Same for `presentation_context.term` (`render.c:3745`). Pane
   callbacks (§5.13) keep `data = term`: `pane_destroy` destroys the callback before the term can go.
3. `fdm_flash` (`terminal.c:432-437`): always read the timerfd and clear `flash.active` (fdm is
   level-triggered; skipping the read busy-spins); gate only `render_overlay` + `wl_surface_commit`.
4. `render_update_title` → `xdg_toplevel_set_title` (`render.c:4349-4361`): for other tabs mark the
   sidebar dirty instead.
5. App-id and icon updates (`render.c:5297`, `:5318`, `:5323`).
6. `ime_update_cursor_rect`.
7. DnD target pick (`selection.c:2745`): filter to visible tabs.
8. `render_resize` tail (`render.c:5049-5053`): `xdg_toplevel_set_min_size`,
   `xdg_surface_set_window_geometry`, `render_refresh_csd`/search only when `tabs_is_active(term)`
   and not `RESIZE_PANE` — otherwise resizing another tab overwrites window state. `tabs_activate`
   step 6 and `tabs_layout` issue them.

### 5.1b Hidden-tab hygiene

- `term_damage_scroll` only merges consecutive same-region entries (`terminal.c:2766-2790`), and
  scroll damage is freed only in `grid_render`/`render_resize`, so a background TUI grows it
  without bound. At the end of `fdm_ptmx` for hidden tabs: `tll_free(grid->scroll_damage)` on both
  grids and `term_damage_view(term)`.
- On hide (`tabs_activate` step 2): `shm_purge(t->render.chains.grid)` after dropping `last_buf`.
  Showing repaints fully anyway, so this frees each hidden tab's buffers at no extra cost.

### 5.2 Tab switch — `tabs_activate(win, new)`

Order matters; each step names its reason. A workspace switch is a tab switch (§5.11), and
switching between split groups hides one group and shows another.

1. `old = win->term`; return if `old == new`. If `new->group && new->group == old->group` →
   `tabs_focus_pane(win, new)`, return (§5.13).
2. `rename_cancel(win)`. Old tab's window-level overlays: `search_cancel(old)`, `urls_reset(old)`
   (pattern `input.c:3250-3251`), unmap scrollback indicator / overlay subsurfaces (attach NULL +
   commit). Also unmap `win->overlay` and `win->render_timer`, set `old->flash.active = false`.
   For every member of the old visible set (old, or its group): `pane_destroy`, purge grid chain
   (§5.1b), `activity_mute_until = now + 500` (focus-out report, §5.14). Disarm the text blink
   timer (`fdm_del(blink.fd)`, `fd = -1`, `state = BLINK_ON`, as `fdm_blink` does); render re-arms
   it on show (`render.c:1084-1087`).
3. `win->term = new; win->ws = new->ws; new->ws->active = new`.
4. Focus: for every seat in `wayl->seats`, `seat_retarget(seat, old, new)` (new, input.c, so the
   static `stop_repeater` and `mouse_button_state_reset` stay private):
   - if `seat->kbd_focus == old`: set `seat->kbd_focus = new`, `stop_repeater`. If
     `seat->ime_focus == old`: `ime_disable(seat)`, `seat->ime_focus = new`, `ime_enable(seat)`
     (`ime.c:414-466`: clears preedit, toggles text-input per `new->ime_enabled`, sends the rect).
   - if `seat->mouse_focus` is any member of the old visible set (a non-focused pane too): set to
     `new`, copy its `active_surface` to `new`, reset it to `TERM_SURF_NONE`, update xcursor,
     `selection_finalize(seat, it, seat->pointer.serial)` (as `wl_pointer_leave`, `input.c:2605`;
     `selection_cancel` would erase a finished selection).
     `mouse_button_state_reset` (`input.c:2410`) only when the pointer is on the main surface's
     grid (unsplit): a sidebar or pane press activates from inside the press handler, and a reset
     there frees the tracked button, so the release is dropped as stray (`input.c:3093-3106`), the
     drag never ends and the double-click count is lost.
     `wl_pointer_leave` asserts the moused term belongs to `win` (§5.13), so re-pointing is required.
   Then, if any seat had the window focused: `term_kbd_focus_out(old)` (returns early while any
   seat still points at `old`, `terminal.c:3490-3492` — hence seats first) and
   `term_kbd_focus_in(new)`. Visual focus: `term_visual_focus_out(old)` and, if
   `win->configure.is_activated`, `term_visual_focus_in(new)`. DEC 2033 visibility report to `new`
   if requested (`wayland.c:1154`). `xdg_surface_configure` (`wayland.c:1150-1157`) keeps doing
   visual focus for `win->term` only.
5. For every newly visible tab: `tab_marker = false`, `tab_activity = false`.
6. Bring `new` up to date with the window: if `new->scale != old->scale` (scale lives in
   `term->scale`; `win->scale` is -1 unless fractional, `wayland.c:2114`) → `term_update_scale` +
   font reload; if its size differs from what `tabs_layout` gives it → `render_resize(..., RESIZE_FORCE)`
   (rare: §5.3 resizes all tabs).
7. If `new` is in a group: create panes + background (§5.13). For every newly visible tab, force a
   full repaint: `render_wait_for_preapply_damage(t)`, `shm_unref(t->render.last_buf)`,
   `t->render.last_buf = NULL` (`force_full_repaint`, `render.c:3238`), `render_refresh(t)`.
8. `render_update_title(new)`, app-id update, `render_refresh_sidebar(win)`, `wayl_win_alpha_changed(win)`
   (opaque region/blur follow `win->term`, `wayland.c:2624`), sidebar refresh (title prefix and
   switcher included).
9. Session dirty.

### 5.3 Resize and scale

All tabs share the window size, so everything that resizes `win->term` resizes every tab, through
`tabs_layout(win, w, h)` (logical):

- First dissolves groups of 1 (`group = 0`): the single place that keeps groups valid after close,
  unsplit, detach, merge, workspace moves.
- Always passes `RESIZE_FORCE`: sidebar show/hide and split changes keep the window size (D4), and
  `render_resize` returns early on an unchanged size (`render.c:4703`).
- Stores `layout_w/h`. Unsplit tab: `render_resize(t, w, h, opts)`. Group member (visible or not, so
  switching back never reflows): `render_resize(t, pane_w, h, opts | RESIZE_PANE)` with
  `pane_w = (w - sb/scale - (n-1)*gap) / n`, `gap` = 4 logical px.
- Then the window tail once: `xdg_surface_set_window_geometry(0, 0, w, h)`, min size (with a visible
  group: `sb + n*pane_min + (n-1)*gap`), background repaint and pane positions if split, sidebar
  show/hide (§6.1), sidebar refresh. No-op while `win->closing`.

Callers:

- `xdg_surface_configure` → `render_resize(win->term, …)` (`wayland.c:1147`) becomes `tabs_layout`.
  On the first configure (`wasnt_configured`, `wayland.c:1181-1182`) call `term_window_configured`
  for **every** tab (restore and early `--tab` attach before configure), unless `win->adopted`
  (§5.10).
- `tabs_relayout(win)` = `tabs_layout(win, tabs_win_size(win))` on tab count/group changes.
  `tabs_win_size`: `layout_w/h` when the visible tab is split, else
  `win->term->width / win->term->scale` and height likewise.
- `surface_enter`/`surface_leave` (`wayland.c:786-822`) edit `win->on_outputs`, not
  `term->window->on_outputs`; they and `surface_preferred_buffer_scale` (`:2091`) return early when
  `win->unmapped` (merge, §5.8 step 4).
- `update_term_for_output_change`: loop over tabs in its four direct callers (`wayland.c:797`, `:818`,
  `:838`, `:2091`, all pass `win->term`); it recomputes per term from its own logical size, right for
  panes too. `update_terms_on_monitor` (`wayland.c:465`) already loops over `wayl->terms`.
- Font size bindings (D5): every tab of the window, then `tabs_relayout`.
- Output removal (`wayland.c:1726`) calls `surface_leave` per terminal: dedupe per window.
- `render_resize` (`render.c:4590`) without `RESIZE_PANE`: `sb = tabs_sidebar_width_px(win)`, applied
  **before** `new_cols` (~`render.c:4730`):
  - `min_width += sb`; `max_pad_x = (width - min_width) / 2`
  - `new_cols = (width - sb - pad_l - pad_r) / cell_width`; `total_x_pad = width - sb - grid_width`
  - `margins.left = sb + (centered ? total_x_pad / 2 : pad_left)`;
    `margins.right = total_x_pad - (margins.left - sb)`; update `xassert(margins.left >= pad_left)`
  - add `sb` once inside `set_size_from_grid()` (~`render.c:4560`; three call sites incl.
    `RESIZE_KEEP_GRID`), subtract it in the `RESIZE_BY_CELLS` snap (~`:4686`)
  - add `sb` to the `CONF_SIZE_PX` default width and the `stashed_width` restore (~`:4623-4660`)
  With `RESIZE_PANE`: `sb = 0`, skip `CONF_SIZE_PX`/stashed defaults, skip the `RESIZE_BY_CELLS` snap,
  skip the tail (§5.1 #8). `send_dimensions_to_client` (TIOCSWINSZ) runs inside for every tab.
- Delayed TIOCSWINSZ: the shared `win->resize_timeout_fd` is registered with `data = term`
  (`render.c:4533`). Register with `win`; `fdm_tiocswinsz` iterates `win->tabs`.
- CSD geometry (`render.c:2406-2421`) reads `term->width/height`: use `tabs_win_size`.

### 5.4 Creating a tab

`term_init` gets a new parameter `struct wl_window *attach_to` (existing callers pass NULL) plus the
target `struct tab_ws *ws` and `bool split` (ignored when `attach_to` is NULL):

- `attach_to` non-NULL: skip `wayl_win_init` (`terminal.c:1461`) and the startup-mode block;
  `term->scale = attach_to->term->scale`. Set `term->window = attach_to` only after the last
  fallible step before `term_font_dpi_changed`/`term_set_window_title` (`slave_spawn`,
  `terminal.c:1444`, is the first `goto err`); everything after the assignment until
  `initialize_render_workers` (`terminal.c:1489`) may still fail, safely, since
  `term_release_window` ignores a term not in `win->tabs`. `tabs_adopt_fonts(term, attach_to->term)`
  copies `font_sizes` (`min(count)` entries per list, arrays sized by each conf,
  `terminal.c:1295-1299`) before `term_font_dpi_changed`. After `initialize_render_workers`:
  `tabs_attach(win, term, after, ws, split)`, then if `win->is_configured`:
  `term_window_configured(term)` (adds the ptmx to fdm). Then `tabs_activate(win, term)`,
  `tabs_relayout(win)`.
- `tabs_attach`: `ws` NULL → `attach_to->ws`. Position: `split` → after the focused pane, `term->group
  = after->group ?: (after->group = ++wayl->group_counter)`; else after the active row's last
  member. `term->ws = ws`.
- New window (`attach_to` NULL): `wayl_win_init` creates no workspace; `term_init` calls
  `tabs_attach(win, term, NULL, tabs_ws_add(win, conf->workspace[0] ? conf->workspace : NULL), false)`
  and sets `win->ws`. Restore passes the saved name instead (§8.3).
- `err:` calls `term_destroy` → `term_release_window` (§5.5), a no-op for a term not in `win->tabs`.
  A failed spawn cannot destroy the shared window. A workspace created for this tab
  (`new-workspace`, `--workspace` step 2) and left empty is dropped by the caller.
- Live cwd of the parent: `/proc/<pid>/cwd` of the foreground process — reuse session.c's
  `proc_chain` (`session.c:606-652`) as `session_live_cwd(term)`; fallback `term->cwd`.

`tab_host.new_tab` implementations:

- **Standalone** (`main.c`): `term_init(&conf, fdm, reaper, wayl, "foot", cwd, NULL, NULL, NULL, argc,
  argv, NULL, &tab_shutdown_cb, &shutdown_ctx, win, ws, split)`. `tab_shutdown_cb` is a no-op (the
  exit code stays the first terminal's); the existing `term_shutdown_cb` (`main.c:134`) does `*ctx->term = NULL`, which
  would make `out:` skip a live tab. Process exit code = first terminal's (§7.3) — the main loop
  condition (`tll_length(wayl->terms) > 0`) already fits.
- **Server** (`server.c`): new `terminal_instance` with `conf = config_clone(parent conf)` — the
  parent instance owns and frees its conf (`server.c:371-389`). `instance_destroy` handles
  `client == NULL` (`server.c:124`). Keybinding tabs go to `server->terminals`; `footclient --tab`
  tabs follow the existing rule. Restored tabs clone `server->conf`. `session_track` the new term.
  Set `wayl->tab_host` before `session_init` (`server.c:670`): restore runs inside it, before
  `server->session` is assigned; `session_window_closing`/`session_tab_moved` return early on a NULL
  session like `session_track`.
  Cloning also keeps `win->term->conf` stable for the CSD size reads (`wayland.c:1118-1122`,
  `:2732`, `:2763`).
- Embedded server (§7.3) does not set `tab_host`: keybinding tabs stay main.c's, client tabs are
  server instances.

### 5.5 Closing a tab / window

URL launcher token callback (`url-mode.c:92-123`) holds `term`, but the token now outlives the
tab (only `wayl_win_destroy` cancels tokens, `wayland.c:2375`): store `win` in the context and
drop the launch unless `term` is still in `win->tabs`.

`fdm_shutdown` (`terminal.c:1633`) and `term_destroy` (`terminal.c:1976-1979`) both call
`wayl_win_destroy(term->window)`. `term_destroy` is also called directly from main.c `out:`,
`server_destroy`, Wayland disconnect and `term_init`'s `err:`. Both call sites become
`term_release_window(term)` (new, terminal.c; ends with `term->window = NULL`). `fdm_shutdown` must
keep releasing: `shutdown_maybe_done` (`terminal.c:1590`) only calls `term_destroy` once
`window == NULL`, so a shutting-down tab leaves `win->tabs` at `fdm_shutdown` time. The seat-pointer
clearing loop in `fdm_shutdown` stays.

`term_release_window(term)`:

- `win == NULL` or `term` not in `win->tabs`: `term->window = NULL`, return.
- If `tll_length(win->tabs) > 1`: `tabs_detach(term)`, then `term->window = NULL`, `tabs_relayout(win)`.
- Else (last tab): `wayl_win_destroy(win, term)`. Signature change from `wayl_win_destroy(win)`
  (`wayland.c:2274`); update all callers. Inside: purge chains of the passed term (NULL = none), not
  `win->term`; set `win->closing` and unlink from `wayl->windows` **before** its `wayl_roundtrip()`
  calls (re-entrant dispatch; target selection must not pick a dying window); destroy panes, sidebar
  subsurface before the parent surface; `shm_chain_free(sidebar_chain)` and `bg_chain` after the last
  roundtrip, before `free(win)` (also on `wayl_win_init`'s error path); free workspaces and
  `rename.buf`; clear `sidebar_drag`. `shm_chain_free` BUGs on leftover buffers, so every tab's
  chains must be purged by its own `term_destroy`.

`tabs_detach(term)` (close and move):

- First, while `term->window` is still set: `search_cancel(term)`, `urls_reset(term)` (`win->urls`
  points into `term->url.list`; `term_destroy`'s own `urls_reset`, `terminal.c:2006`, runs after
  the release and is a no-op without a window).
- Unlink from `win->tabs`; `pane_destroy(term)`; if `sidebar_drag.tab == term`, clear the drag.
- `win->closing`: nothing else (no activation, relayout or workspace bookkeeping; workspaces are
  freed in `wayl_win_destroy`).
- Workspace now empty: drop it (`free(name)`; `rename_cancel` if it pointed there); if it was current,
  activate the next workspace's `active` (else previous). Else if `term` was `ws->active` of a
  non-current workspace: set it to the neighbour.
- `term == win->term` in a non-empty workspace: activate a neighbour — in the group (right, else
  left), else the row below in the same workspace, else above; skip `shutdown.in_progress` tabs; if
  only those remain, leave `win->term` (each releases itself; the last destroys the window).
- Purge the term's own chains (`shm_purge` for each `term->render.chains.*`); clear any seat
  pointer still at `term`.

Other rules:

- `fdm_hook_refresh_pending_terminals` (~`render.c:5204`) is only safe because it checks
  `shutdown.in_progress` before dereferencing `term->window`; keep that order.
- Teardown of N tabs runs N sequential reaps (each with the 60 s alarm). Acceptable; on window
  close SIGHUP reaches all slaves at once, since `term_shutdown` on all tabs runs first.
- Window close (`xdg_toplevel_close`, CSD close, `quit`): `tabs_close_window(win)` sets
  `win->closing = true`, calls `tab_host.window_closing`, then `term_shutdown` on every tab (iterate
  a copy). The last one to finish destroys the window.
- `hold_at_exit` tabs stay until closed, unchanged semantics.

### 5.6 Titles and markers

- `term_set_window_title` (`terminal.c:3813`) → `render_refresh_title`: still runs for all tabs;
  `render_update_title` (§5.1 #4) sets the toplevel title only for the active tab, and for every tab
  refreshes the sidebar.
- Title to the compositor: `"%s: %s", win->ws->name, title` when the name is non-NULL (D12).
- `term_bell` (`terminal.c:3908`): if `!tabs_is_visible(term)` → `tab_marker = true`, sidebar dirty
  (chip marker included). Window urgency only if no seat has this window focused (today's check is
  `term->kbd_focus`, false for other tabs even in a focused window).
- Notifications "focus" action (`notify.c:274-279`): `tabs_activate(term->window, term)` in both
  branches, before `wayl_activate`; skip if `term->window == NULL`. `inhibit_when_focused`
  (`notify.c:359`) checks `term->kbd_focus`, so other tabs in a focused window still notify —
  intended.

### 5.7 Other single-term assumptions to fix

- `main.c` `out:` (`main.c:710-719`) and `wayl_destroy` (`wayland.c:1977`) destroy one term.
  Replace with `while (tll_length(wayl->terms) > 0) term_destroy(tll_front(wayl->terms))` after
  `server_destroy` (which already runs first and destroys its instances' terms).
- SIGUSR1/2 theme switch: 1.28 `sigusr_context` is `{term, server}` (`main.c:50-53`) and `term`
  dangles once `term_shutdown_cb` NULLs main's `term`. Change it to `{wayl, server}`; `fdm_sigusr`
  (`main.c:56-75`) always iterates `wayl->terms`. Drop the server branch: a standalone foot with an
  embedded server has terms in both, and `wayl->terms` holds every server terminal. Keep setting
  `server->conf->initial_color_theme` when a server exists.
- Keybinding sets are per (seat, conf) (`key-binding.c:110`, `input.c:1644`) and looked up from the
  active term; tabs with different confs (server clones) still work.

### 5.8 Merge window — `tabs_merge_into(src, dst)`

1. Target: highest `focus_seq` window that is not `src`, not `closing`, and configured. None → no-op.
2. `rename_cancel(src)`. `moved_active = src->term`. Workspace map (array of src→dst pairs, ≤64):
   per src workspace, `dst_ws = name ? tabs_ws_find(dst, name) : NULL`, else `tabs_ws_add(dst,
   name)`; a newly created dst workspace takes the moved `src_ws->active` as `active`. Unnamed src
   workspaces stay separate. For each tab `t` of `src` in order:
   `tabs_transfer(t, dst, map(t->ws), t == moved_active)` (§5.9). `moved_active` keeps its seat
   pointers: `wayl_win_destroy`'s roundtrips dispatch queued input (the merge chord's key release)
   into `key_press_release`/`wl_pointer_button`, which need a non-NULL term, and `keyboard_leave`
   asserts against `src->term` (`input.c:779-781`); the compositor's leave does its focus-out.
   Groups move intact (ids are global). No per-tab resize: step 5's `tabs_relayout` resizes them all.
3. Session: `tabs_transfer` moved each tab record via `tab_moved` (§8.2); drop `src`'s empty record
   with no grace.
4. First `src->unmapped = true` and destroy/NULL `src->frame_callback`: its own destroy
   (`wayland.c:2393`) comes after the roundtrips (`:2345`, `:2351`), during which the handler would
   render `moved_active` onto `dst` and a configure would restart its blink. Then
   `wayl_win_destroy(src, NULL)` — no `term_shutdown` of the moved tabs; it never reads `src`'s
   workspaces, which are freed after it. Leave `src->term` at `moved_active` until it returns: it
   dereferences `win->term->wl` throughout (`wayland.c:2274-2410`). Afterwards
   `term_visual_focus_out(moved_active)`. `csd_destroy` (`wayland.c:90-100`) frees
   `term->window->csd.font`, now `dst`'s: change it to `win->csd.font`, and check every other
   `win->term->…` read in `wayl_win_destroy` the same way (only `->wl` and
   `render_wait_for_preapply_damage` are window-independent; `shm_purge(term->render.chains.csd)` on
   `moved_active` only drops a cache). The roundtrips also dispatch `wl_surface` enter/leave for
   `src`, hence the `unmapped` guards in §5.3.
5. `tabs_activate(dst, moved_active)` (switches dst to its workspace), `tabs_relayout(dst)`. No
   `wayl_activate`: a no-op without a token (`wayland.c:2919`); the compositor picks focus after
   `src` closes and `keyboard_enter` targets `dst->term`.

### 5.9 Shared move — `tabs_transfer(t, dst, dst_ws, keep_focus)`

1. `search_cancel(t)`, `urls_reset(t)`, `selection_cancel(t)` (subsurfaces belong to the old window,
   `wayland.c:2358-2363`).
2. `!keep_focus`: `term_kbd_focus_out(t)`, `term_visual_focus_out(t)`.
3. `tabs_detach(t)` (unlinks, destroys the pane, src workspace bookkeeping), `t->window = dst`,
   `t->ws = dst_ws`. Groups of 1 left in src dissolve at src's next `tabs_relayout`, so moving a
   whole group one member at a time keeps its id.
4. `dst->term != t` (merge): `tabs_adopt_fonts(t, dst->term)`; `old = t->scale`;
   `term_update_scale(t)`; `if (!term_font_dpi_changed(t, old)) reload_fonts(t, false)` (export it,
   `terminal.c:1016`; adopted `font_sizes` need loading even when scale and DPI are unchanged).
   `dst->term == t` (detach into a fresh window): fonts stay; scale follows the new surface.
5. Purge grid chain, drop `last_buf`; `tll_push_back(dst->tabs, t)`. If `dst->term == t`:
   `dst->ws = dst_ws; dst_ws->active = t`.
6. `tab_host.tab_moved(data, t, dst)` if set (§8.2).

No resize: the caller's `tabs_relayout` (merge) or first configure (detach) does it.

### 5.10 Detach — `tabs_detach_window(t, whole_group)`

Triggers: `detach-tab` (focused pane alone) and sidebar drag-out (`whole_group`, §6.7).

1. `src = t->window`; `set` = `t`, or its group's members in order when `whole_group`. No-op if
   `set` covers all of `src->tabs`, `src->closing`, or `t->shutdown.in_progress`.
2. If `src->term` is in `set`: `tabs_activate(src, neighbour)` — the nearest tab not in `set` (group
   neighbour first for a single pane, else row below, else above, else another workspace's active).
   §5.2 #4 moves every seat's kbd/mouse focus there, so the chord's key release (or the drag's
   button release) lands on the neighbour.
3. `new = wayl_win_init(set[0], NULL, NULL)` (`wayland.c:2099`). It reads only `term->wl`,
   `term->conf`, `term->app_id`, never `term->window`, and does not touch `tabs` or workspaces.
   NULL → return false; nothing changed yet. Its `out:` path relies on T13's
   `wayl_win_destroy(win, NULL)` not shutting down the term.
4. `new->adopted = true`; `ws = tabs_ws_add(new, t->ws->name)` (a fresh window cannot collide);
   `tabs_transfer(m, new, ws, false)` for each member `m` of `set`. A single pane detached from a
   group: `m->group = 0` first.
5. `term_set_window_title(new->term, new->term->window_title)`: xdg title is per toplevel.
6. `tabs_relayout(src)`.
7. Rendering stays gated until `new` configures (`render.c:4595`, `:5207`, `terminal.c:528`); ptmx
   keeps reading. `xdg_surface_configure` skips `term_window_configured` when `adopted`: the ptmx is
   already in the fdm and a second `fdm_add` fails with `EEXIST` (`fdm.c:192`). Likewise
   `term_shutdown` (`terminal.c:1738`) does `fdm_del` when `is_configured || adopted`, else it
   `close()`s a registered fd. The first configure's `tabs_layout` sizes the moved tabs.
8. No `wayl_activate`: no token. niri focuses new toplevels by default.

### 5.11 Workspaces

- `tabs_select_ws(win, ws)` = `tabs_activate(win, ws->active)`: focus handover, repaint, search
  cancel all apply. `select-workspace-N` / `next`/`prev-workspace` map onto it.
- `new-workspace`: `ws = tabs_ws_add(win, NULL)`, then `tabs_new(win->term, ws, false)`; on failure
  drop `ws`.
- `tabs_ws_set(term, ws)` (`move-tab-to-workspace-N`, chip drop): moves the row (whole group) to the
  end of `win->tabs` in order — rows are filtered by workspace, so that appends within `ws`; sets
  `ws` on each member; drops the emptied source; then `tabs_activate(win, term)` (follow).
- `next-tab`/`prev-tab`/`select-tab-N`/`move-tab-*` use `tabs_row_*`, which iterate rows of
  `win->ws` only; `tabs_move` swaps the active row with the neighbouring row of the same workspace.

### 5.12 Inline rename

- `rename_begin(win, ws)`: copy the name into `buf` (`ambstoc32`, char32.h), cursor at end, sidebar
  dirty. Leaves search/URL mode alone: the sidebar is not their surface.
- Key dispatch: `input.c` key handler, before the `unicode_mode` branch (`input.c:1648`):
  `if (term->window->rename.ws) { if (pressed) { if (should_repeat) start_repeater(...);
  rename_input(...); } return; }`. Bindings are skipped while renaming.
- `rename_input`: keysym switch shaped like `unicode_mode_input` (`unicode-mode.c:44`):
  `Return`/`KP_Enter` commit, `Escape` cancel, `BackSpace`/`Delete` remove a char,
  `Left`/`Right`/`Home`/`End` move, `Control+u` clear. Otherwise text: the compose/utf8 block of
  `search.c:1482-1504`, then `mbsntoc32` insert at the cursor as in `search_add_chars`
  (`search.c:623-660`). About 15 lines duplicated rather than a shared API. Reject chars `< 0x20`;
  cap 64 chars.
- Commit: `ac32tombs` (`char32.h:111`). Empty → NULL. Equal to another workspace's name in the
  window → field stays open (D14). Else replace; title + sidebar refresh, session dirty, end.
- Cancel: free `buf`, end, sidebar dirty.
- Commit and cancel both `stop_repeater`: a held Return would otherwise repeat into the pty.
- IME (`ime.c` `done`): commit branch (`ime.c:196-206`) → `rename_add_utf8` instead of
  search/`term_to_slave` while renaming; then `ime_reset_pending_preedit(seat)` and return before
  step 5, so no preedit cells are built. Cursor rectangle
  unchanged (candidate popup at the grid cursor). Accepted.
- Ends on `tabs_activate` (§5.2 #2), workspace dropped, merge, window destroy. Keyboard leave does
  not end it.

### 5.13 Split view

- **Model.** Members of a group share `term->group` and `term->ws`, are contiguous in `win->tabs`;
  order = left-to-right. Ids come from `wayl->group_counter`, so merge and detach need no remap.
  Visible = `win->term` plus its group.
- **Surfaces.** An unsplit tab renders into `win->surface` as today. A visible group of n≥2: each
  member gets `term->pane` from `wayl_win_subsurface_new(win, &term->pane, true)` (`wayland.c:2814`),
  `wl_subsurface_set_desync`, at `(sb + i*(pane_w + gap), 0)` logical. Created on show, destroyed on
  hide (`pane_destroy`: destroy `pane_cb`, the subsurface, drop `last_buf`). `win->surface` gets a
  window-size background buffer from `bg_chain` filled with `win->term`'s background (alpha
  honoured), repainted on layout, scale and colour change, damaged whole.
- **Grid path.** `term_surf(term)` = `term->pane.surface.surf ?: term->window->surface.surf`, used in
  place of `term->window->surface.surf` for damage (`render.c:1346-1360`, `:1468`, `:1545`,
  `:1935`, `:3656`, `:3766`), attach/commit (`:3769-3770`) and scale (`:2439`, `:2542`).
  `term_frame_cb(term)` = `&term->pane_cb` when it has a pane, else `&win->frame_callback`; used at
  `render.c:3729`, in `frame_callback` (`render.c:4366-4410`) and in the "render now if no
  callback" test of `fdm_hook_refresh_pending_terminals` (`render.c:5204-5255`). No presentation
  feedback for panes (`render.c:3739`). After a pane commit, `wl_surface_commit(win->surface)`
  (no new buffer): sidebar, search, URL, overlay, indicator and CSD are sync subsurfaces of the
  main surface and apply only on its commit.
- **Window callback while split:** `frame_callback` (window listener) finding `win->term` with a
  pane destroys itself and returns; unsplit re-arms through the normal path.
- **Window subsurfaces** showing per-term content are offset by `term_pane_x(term)` (0 unsplit):
  scrollback indicator `render.c:3174`, render timer `:3217`, search `:4093`, URL labels `:4335`,
  overlay `:2005`/`:2214` (also sized to the pane). IME cursor rect (`ime.c:76`, `:487`) adds
  `term_pane_x(term) * scale` to x. They follow `win->term`; §5.2 step 2's overlay
  cleanup also runs on pane focus change.
- **Input.** Pane surfaces keep `user_data = win`, so the `wl_surface_get_user_data` sites
  (`input.c:713`, `:781`, `:2477`, `:2586`, `:3556`, `:3588`, `:3631`, `ime.c:59`, `wayland.c:2294`)
  still get a window. `tabs_term_for_surface(win, surface)`: the member whose `pane` matches, else
  `win->term`; used for pointer enter (`input.c:2477-2481`) and touch down (`:3556`), which stores
  it in a new `seat->touch.term`; touch up/motion (`:3588`, `:3631`) use that instead of
  `win->term`, so a touch that started on a pane stays there.
  `term_surface_kind` (`terminal.c:4590`): `TERM_SURF_GRID` for a pane; the main surface returns
  `TERM_SURF_NONE` while split. Relax `xassert(old_moused == win->term)` (`input.c:2587`) to
  `old_moused->window == win`. Keyboard enter stays on `win->term`. Button press on
  `TERM_SURF_GRID` (`input.c:3248`) with `term != win->term` → `tabs_focus_pane(win, term)` first,
  then normal handling.
- **Pane focus** `tabs_focus_pane(win, t)`: §5.2 steps 2 (overlays only; panes stay), 3, 4, 8, 9.
  No repaint: both panes stay on screen; old shows the unfocused cursor.
- **Actions.** `split-new`/`split-next` refuse (bell) when `pane_w` would fall below
  `render_resize`'s `min_width` for `n+1` panes. `split-new` = `tabs_new(from, from->ws, true)`.
  `split-next`: the next row (whole group) joins: set its `group`, relayout. `unsplit`: `group = 0`
  on all members, relayout. `close-tab` closes the focused pane (§5.5 neighbour rule).
  `move-tab-*`, `move-tab-to-workspace-N` and drag move the whole group; `detach-tab` the pane.

### 5.14 Activity marker

- `fdm_ptmx` (`terminal.c:246`): set `got = true` on `count > 0` in the read loop
  (`terminal.c:277-298`). After the loop: if `got && conf->tabs.activity && term->window &&
  !tabs_is_visible(term) && !term->tab_activity && now_ms() >= term->activity_mute_until` →
  `tab_activity = true`, `render_refresh_sidebar(win)`. Edge-only, so
  a busy tab costs one clock read per wakeup.
- Mute (`activity_mute_until = now_ms() + 500`) where foot provokes output: `tiocswinsz`
  (`render.c:4414`, every SIGWINCH path incl. the shared timer, `render.c:4489-4559`), theme switch
  reports (`terminal.c:4921`, `:4941`), and §5.2 step 2 (hide). No marking until a tab
  has been shown once (`term->tab_shown`, set in §5.2 step 5): covers restored tabs' startup output.
- Cleared in §5.2 step 5. Not counted: blink and render timers (no pty read). Interactive resize
  defers reads (`terminal.c:265-273`); the mute covers the burst after.
- `now_ms()`: `clock_gettime(CLOCK_MONOTONIC)`, static in `tabs.c`.

## 6. Sidebar

### 6.1 Surface lifecycle

- Created in `tabs_layout` when ≥2 tabs, fullscreen included.
- `wayl_win_subsurface_new(win, &win->sidebar, true)` (`wayland.c:2814`). Synchronized subsurface:
  its commit applies on the next main-surface commit, so sidebar and grid update atomically. While
  split, the main surface commits with the background repaint on every layout/sidebar change.
- Position (0, 0) relative to the main surface; above it.
- Destroyed when tabs drop to 1 (purge `sidebar_chain`) and in `wayl_win_destroy` (§5.5).
- `term_surface_kind` (`terminal.c:4590-4612`): `TERM_SURF_SIDEBAR` — else `wl_pointer_enter`
  hits `BUG()` (`input.c:2525`).

### 6.2 Geometry

Physical pixels (scale-aware like `get_csd_data`, `render.c:2402-2410`):

```
w = roundf(conf->tabs.width * win->term->scale)
h = main buffer height (incl. margins)
row_h = term->fonts[0]->height + 2 * roundf(4 * win->term->scale)
tab rows from y=0 for win->ws only; '+' row after the last;
switcher row at h - row_h (when shown) with a 1px separator above; rows clipped above it (§6.5)
```

The main buffer width must be divisible as `wayl_surface_scale` requires (`wayland.c:2557-2589`);
use the same rounding for w and position so the sidebar edge meets the grid without a gap.

### 6.3 Drawing — `render_sidebar(struct wl_window *win)`

- `win->sidebar_chain` is created once in `wayl_win_init`, bit depth
  `shm_chain_bit_depth(term->render.chains.grid)` (`shm.c:1136`). `shm_get_buffer(sidebar_chain, w, h)`.
- Colours from the active tab: bg = `color_blend_towards(colors.bg, colors.fg, 1.1)` (`render.c:327`),
  alpha = `colors.alpha`, forced 0xffff when fullscreen (`render.c:1299-1308`) with an opaque region
  then; gamma via `wayl_do_linear_blending` like the OSD. Active row bg = `colors.selection_bg` if
  custom (`(selection_bg >> 24) == 0`, `render.c:798-822`), else fg/bg inverted; accent bar =
  `colors.cursor_bg` if bit 31 set, else `colors.fg` (`render.c:648-662`); text = `colors.fg`. On
  the active row with inverted colours, accent and text = `colors.bg`; with custom selection, text =
  `selection_fg` if `(selection_fg >> 24) == 0`. Bell `•` = `colors.table[3]`, activity `◦` =
  `colors.table[4]`. Chips as rows; current chip as the active row.
- Rename field: bg `colors.bg`, text `colors.fg`, 1px cursor bar (cursor colour rule) at the measured
  advance of `buf[0..cursor)`; text scrolls left when the cursor passes the right edge.
- Dragged row while `sidebar_drag.out`: bell-marker colour.
- Under Vulkan: call `render_sidebar` outside `vkr_begin`/`vkr_end` (`render.c:3398-3411`, `:3761-3775`).
- Text with fcft like `render_osd` (`render.c:2458`): `fcft_rasterize_text_run_utf32` when
  available, else per glyph. Truncate by measuring advance; append `…`.
- `wayl_surface_scale` + attach + damage + commit (pattern `csd_commit`, `render.c:2437`).
- Trigger: `render_refresh_sidebar(win)` (`render.c`/`render.h`): sets `win->sidebar_dirty` and
  `win->term->render.refresh.csd = true` with no `csd_mode` gate — `render_refresh_csd`
  (`render.c:5367-5371`) only sets it under `CSD_YES`, so under SSD the sidebar would never repaint;
  `render_csd` keeps its own gate. Not `render_refresh`: the
  hook skips a tab unless grid|csd|search|urls is set, and with app-sync updates active only
  csd|search|urls pass (`render.c:5215-5219`); the synchronized sidebar only shows on a main-surface
  commit, which `refresh.csd` forces. Call `render_sidebar` beside `render_csd` in both hook branches
  and in `frame_callback` (`render.c:4392`), also when `csd_mode != CSD_YES`. Dirty sources: tab
  add/remove/move/activate, group change, title change, markers, workspace add/drop/rename/switch,
  rename edits, drag state, resize, scale, font size, colour change.

### 6.4 Pointer input

`input.c`: `TERM_SURF_SIDEBAR` cases in `wl_pointer_enter` (`:2504`, default cursor), `leave`
(`:2594`, cancels a drag), `motion` (`:2679`, `:2715`, drag tracking §6.7), `button`
(`~3112-3299`, BUGs on unknown at 3299). Act on press (left: activate / `+` / chip, arm drag;
middle: close); release ends a drag. Hit test: switcher if shown and `y >= h - row_h`, chip =
`x / (w / count)`; else row = `(seat->mouse.y * scale) / row_h + sidebar_scroll`, mapped through
`tabs_row_term`. Click on a tab row while renaming: cancel, then the normal action.
Wheel: `mouse_scroll` (`input.c:3327`) returns early unless `active_surface == TERM_SURF_GRID`.
`term_xcursor_update_for_seat` (`terminal.c:3761`): left_ptr, `grabbing` while dragging.

Touch: `touch_down/up/motion` (`input.c:3547-3670`) synthesise pointer buttons, then restore
`seat->mouse_focus` (`input.c:3616`, `:3664`) and `active_surface` to the pre-call term only if
`seat->mouse_focus` still equals the term the handler set: a tap that ran `tabs_activate` or a
drag-out retargeted the seat, and restoring over it trips the `wl_pointer_leave` assert.
Before destroying a sidebar or pane subsurface, clear `touch.surface`/`touch.term` on every seat
whose `touch.surface` is it and set `touch.state = TOUCH_STATE_IDLE` if above idle (up/motion
would read a freed or NULL surface).

### 6.5 Scrolling the list

If rows don't fit above the switcher, set `sidebar_scroll` so the active row is visible after every
activation and move.

### 6.6 Scale and fullscreen

Re-render on `win->term->scale` change: `render_refresh_sidebar(win)` beside the existing
`render_refresh_csd` after scale changes. Fullscreen: sidebar stays; mark it dirty when `xdg_surface_configure` flips
`is_fullscreen` (alpha forced to 0xffff).

### 6.7 Drag to reorder

- Left press on a tab row: activate (unchanged), then arm `sidebar_drag` (`seat`, `tab` = row's
  first member, `start_y`). `+`, chips, middle click: no arming.
- Motion, same seat: `|y - start_y| >= row_h / 2` → `dragging = true`, cursor `grabbing`. While
  dragging: `out = x < 0 || x >= sidebar_w || y < 0 || y >= h`; if inside and over a tab row, call
  `tabs_move(win, ±1)` until the active row is at the row under the pointer (clamped). Live reorder,
  no drop indicator. `tabs_move` keeps the active row visible (§6.5), which gives edge autoscroll.
- Motion and release outside the sidebar still arrive: the press gives the sidebar subsurface an
  implicit grab, with unclamped surface-local coords (`input.c:2668-2669` are plain `int`).
- Left release: `dragging && out` → `tabs_detach_window(tab, true)`; `dragging` over a chip other
  than the current → `tabs_ws_set(tab, chip_ws)`. Always clear `sidebar_drag`. Release without
  `dragging` does nothing.
- Cancel without action: `wl_pointer_leave` of the sidebar (compositor broke the grab);
  `tabs_detach(sidebar_drag.tab)` (shell exits mid-drag); `wayl_win_destroy`.
- Touch: `wl_touch_motion` already synthesises press + motion for non-grid surfaces
  (`input.c:3645-3652`) and release in `wl_touch_up` (`:3598-3602`); covered by the pointer path plus
  the §6.4 restore guard.

## 7. Command line and server

### 7.1 Protocol

`client-protocol.h`: `bool tab:1;` takes one bit from `reserved:5` → `reserved:4`. footclient sets it
for `--tab` and for `--workspace`. `--workspace` rides in overrides (D6). Server reads the bit in
`fdm_client` (`server.c:303-364`).

### 7.2 Server handling of `--tab`

In `fdm_client` before `term_init`, if `tab`: `win = tabs_find_target(wayl, conf->workspace, &ws)`:
1. workspace given: window with a workspace of that name (highest `focus_seq`), `ws` = it.
2. given, no match: highest-`focus_seq` window; `ws = tabs_ws_add(win, name)`.
3. none given: highest-`focus_seq` window, `ws = win->ws`.
4. no window (closing and unconfigured skipped): NULL → normal new window, first workspace =
   `conf->workspace`.

Then `term_init(..., attach_to = win, ws, false)`, `wayl_activate(wayl, win, token)` (`wayland.h:577`).
If `term_init` fails after step 2 created `ws`, drop it. The instance keeps its client (so
`footclient --tab cmd` waits and returns the exit code).

`focus_seq`: in `keyboard_enter`, `win->focus_seq = ++wayl->focus_counter`.

The server only sees the merged conf, so a foot.ini `workspace=` makes every `--tab` land in that
workspace. Documented.

### 7.3 Standalone `foot --tab`

Paths (only when `XDG_RUNTIME_DIR` is set; no `/tmp` fallback, unlike `get_server_socket_path`,
`config.c:3397`):
- own socket: `$XDG_RUNTIME_DIR/foot-tab-$WAYLAND_DISPLAY-<pid>.sock` (standalone only; a server
  keeps its existing path).
- pointer: `$XDG_RUNTIME_DIR/foot-tab-$WAYLAND_DISPLAY.sock` → own socket of the last-focused foot.

Listening side (standalone that did not hand off):
1. After `term_init` (`main.c:655`): `server = server_init(&conf, fdm, reaper, wayl, own_path,
   embedded = true)` (`server.c:593`). New params: explicit path (skips `get_server_socket_path`) and
   `embedded` (skips socket activation, `session_init`/restore and `tab_host`). Failure → `LOG_WARN`,
   continue with `server = NULL`. `own_path` is heap, freed after `server_destroy` (`server_init`
   stores the pointer, `server.c:661`); `server_init`'s `err:` already closes the fd.
2. Main loop unchanged (`main.c:703`): the process lives while `wayl->terms` is non-empty. Exit code
   stays the first terminal's (`term_shutdown_cb`, `main.c:131`).
3. `out:` already calls `server_destroy` first (unlinks own socket, `server.c:709-710`).
4. Client requests take the normal server path (§7.2), including the new-window case.

Pointer upkeep (server and embedded; not socket-activated servers, whose path is not ours):
- `keyboard_enter`, after `focus_seq`: if `wayl->tab_sock_path && !wayl->tab_sock_owner`:
  `symlink(own, ptr.<pid>)`, `rename(ptr.<pid>, ptr)` (atomic); `tab_sock_owner = true` on success.
  Any other process's focus doesn't clear our flag, so also re-check with `readlink` when the flag
  is set — one syscall per focus.
- `server_destroy`: `readlink(ptr) == own` → `unlink(ptr)`. Race with another process repointing in
  between: harmless, its next focus restores it.

Access: `fdm_server` (`server.c:450`) after `accept4`: `getsockopt(SO_PEERCRED)`; `uid != getuid()`
→ close. Covers a non-0700 `XDG_RUNTIME_DIR` and the normal server too.

Client side (`main.c`, after option parsing, before `wayl_init`):
1. `--tab` with `XDG_RUNTIME_DIR`: `connect()` to the pointer. Fail (ENOENT, ECONNREFUSED from a
   stale link) → continue as a normal standalone foot.
2. Success: close, `setenv("XDG_ACTIVATION_TOKEN", token)` if one was saved (`main.c:205-206`
   unsets it), `execvp("footclient", argv2)`; fail → `LOG_WARN`, continue standalone. `argv2` =
   `footclient --server-socket=<ptr> --tab -E` + forwarded options + `--` + command. Forwarded
   (`client.c:157-209`): `--workspace`, `-o`, `-T`, `-a`, `-D`, `-H`, `-t`, `-w`, `-W`, `-m`, `-F`,
   `-L`, `-d`, `-l`. Other foot options with `--tab` (`-c`, `-f`, `-s`, `-p`…): warn "ignored with
   --tab". cwd (`client.c:429-460`) and exit code come with footclient.

Target choice: the pointer names the last-focused process, which picks a window by §7.2. A
`--workspace` that exists only in another process is not found there; it is created in the
last-focused process (non-goal, §1). ponytail: per-process lookup; add a workspace→socket map if
users run many standalones.

### 7.4 Options

- foot: long-only `--workspace` (enum like `TOPLEVEL_TAG_OPTION`, `main.c:214-260`) → override;
  long-only `--tab` (§7.3); `--tab` with `--server` or `--pty`: error, exit 1 (`main.c:439-441`).
- footclient: `--tab` (long only); `--workspace=NAME` → override and `tab = true`. `-o workspace=`
  alone does not set the bit.
- Version skew: after `dnf upgrade` an old running server ignores the tab bit → new window. Document
  in footclient(1).

## 8. Session restore (format v5)

### 8.1 Schema

```
FOOT-SESSION 5
<xdg_id blob>
<window count>
per window:
  <name blob>          toplevel id (one per window)
  <ws count>\n         1..64
  <current ws index>\n
  per workspace:
    <ws name blob>     "" = unnamed
    <active index>\n   within this workspace
    <tab count>\n      ≥1
    per tab:
      <group>\n        0 = none; file-local id
      <cwd blob> <snapshot blob> <launch argv> <command count> { <cwd blob> <argv> }*
```

Limits: tabs per window ≤ 256 (sum). Reading v2–v4: each record becomes a window with one unnamed
workspace and one tab (keep the `version` switch in `read_window`, `session.c:405-442`).

### 8.2 Tracking

Split `session_tracked` (`session.c:90-99`):

- `session_window_tracked`: `struct wl_window *win`, name (toplevel id), closed-grace bookkeeping,
  `bool closing`, owns xdg `add_toplevel`/`remove_toplevel` (`session.c:1445-1462`, `:1481`).
- `session_tab_tracked`: `struct terminal *term`, launch argv, restore_commands, relaunch cache,
  `saved` snapshot, back-pointer to its window record.

`session_track(term)`: find (skipping `closing` records: a freed `win` address may be reused) or
create the window record for `term->window`, append tab.
`session_untrack` normally runs after `term_destroy` (`shutdown_maybe_done` → `term_shutdown_handler`
→ `instance_destroy`, `server.c:140-146`), when `term->window` is NULL and the window may be freed:
never dereference it. The window record carries its own `closing`, set by
`session_window_closing(s, win)` (pointer compare, no deref) via `tab_host.window_closing`.
Untrack reaches the record via the tab's back-pointer.
- Record `closing`: keep the tab record; when the last tab leaves, move the window record with its
  tabs' `saved` snapshots to the 5 s closed-grace list (`session.c:477-485`).
- Otherwise drop the tab record and free its `saved`; never push it to `closed` (`session.c:1481-1495`
  applies only at window granularity, or a closed tab would come back as a one-tab window).
- Window record with no tabs left and `!closing`: drop with `remove_toplevel`.
- Move (merge, detach): `session_tab_moved(s, term, dst)` via `tab_host.tab_moved` moves the tab
  record to `dst`'s window record, creating it (`add_toplevel`) if `dst` has none. The emptied source
  record is dropped without grace (merge); detach never empties it.
- Shells killed by SIGHUP before foot sees a window close are not `closing`: their tabs are dropped
  one by one. Accepted.

`session_destroy` (`session.c:1377`) clears `->session` on every window and tab record:
`server_destroy` runs it before `instance_destroy`, so later untracks are no-ops.

Save: workspaces in `win->workspaces` order; per workspace its tabs filtered from `win->tabs`, with
`group`. `build_window` can return NULL (`session.c:985-1120`): indices and counts count only tabs
with a snapshot (active falls back to 0); a workspace with none is skipped (current falls back to 0);
a window with none is skipped. Order, active, current and groups are read at save time, not cached.
Session dirty on: activate, move, group change, workspace add/drop/rename. The closed-grace entry
holds the whole window record.

### 8.3 Restore

`restore()` (`session.c:1292-1322`) calls `session_restore_cb(data, session, w, cwd, argv)`
(`session.h:15`) once per window. It loops tabs inside each window instead; the callback gains
`struct wl_window *attach_to` (NULL for the first tab, then the window the first call created) and
the workspace name. Every tab gets its own instance pushed to `server->terminals`, so
`instance_destroy` and `session_untrack` stay balanced per tab.

`restore_window` (`server.c:569-592`): the first tab with `term_init(..., toplevel_name,
attach_to=NULL)` and its workspace name (§5.4; niri restores placement by toplevel id); the rest with
`attach_to = first->window` and `ws = tabs_ws_find(win, name) ?: tabs_ws_add(win, name)` (unnamed:
one new workspace per saved unnamed workspace, tracked by index). After all tabs: groups assigned
(file-local ids remapped to `++wayl->group_counter`), each workspace's `active` = its saved index,
`tabs_activate` the current workspace's active tab, `tabs_relayout`. Each tab gets its own restore
script (`session.c:1210-1258`). If a tab fails to start, continue; the first tab that succeeds
creates the window. Each tab's snapshot file is cleaned up independently.

Logout rule (`session.c:1104-1110`): already per tab; no change.

## 9. Docs, completions, config

- `doc/foot.ini.5.scd`: `[main] workspace` (D6), `[tabs] width`, `[tabs] activity`, all new actions,
  rename keys.
- `foot.ini`: commented examples (`select-workspace-1=Control+Shift+F1`,
  `rename-workspace=Control+Shift+F2`, `split-new=…`).
- `doc/foot.1.scd`: `--workspace`, `--tab` (forwarded options, fallback, `XDG_RUNTIME_DIR`),
  sidebar paragraph (drag, detach, double-click rename). `doc/footclient.1.scd`: `--tab`,
  `--workspace` implies `--tab`, version-skew note.
- Completions: `completions/{zsh/_foot,zsh/_footclient,fish/foot.fish,fish/footclient.fish,bash/foot,bash/footclient}`
  (bash: add `--workspace` to the arg regex, `footclient:39`).
- Config parse: `binding_action_map` (`config.c:125-215`), defaults (`config.c:3441`), `[tabs]`
  section parser. New `BIND_ACTION_*` entries go after `BIND_ACTION_THEME_TOGGLE`, before the mouse
  block; redefine `BIND_ACTION_KEY_COUNT` as last new action + 1 (`key-binding.h:62`; `config.c:2571`
  and test-config iterate up to it).
- `char *workspace` in `struct config`: default `xstrdup("")` like `toplevel_tag` (`config.c:3573`),
  copy in `config_clone` (`:3985-4000`, §5.4 depends on it), free in `config_free` (`:4108`),
  `value_to_str` case (`:968`). Options follow `--toplevel-tag` (`main.c:191,222,294`).

## 10. Packaging

- Work tree: git repo of `foot-1.28.0` + Patch0 + Patch1 committed as base; tabs work on a branch;
  `git diff base > foot-tabs.patch`.
- `foot.spec`: `Patch2: foot-tabs.patch`, `tabs.c` in `meson.build` (inside the patch), `Release: 11`,
  changelog bullets (`- Add vertical tabs with sidebar`, `- Add workspaces`, `- Add split view`,
  `- Add tab drag and detach`, `- Add foot/footclient --tab`, `- Session state v5`).
- Release: commit, `mx-rpm -S --no-git-commit --copr lacamar/arm64-misc --copr-wait --install foot.spec`
  (tag `foot-1.28.0-11` made by mx-rpm).

## 11. Verification

Unit (meson `tests/`):
- `test-config`: new keys and actions parse; defaults present.
- No session unit test: session.c needs most of foot linked and `%check` runs `%meson_test`.
  v5 round-trip and v4 load are manual checks 13 and 26.

Manual on niri (both renderers: `[tweak] renderer=pixman` and `vulkan`), screenshot via
`niri msg action screenshot-window`:

Tabs:
1. Single tab looks identical to stock (no sidebar, same cols).
2. `Ctrl+Shift+t`: sidebar appears, grid narrows, `tput cols` in both tabs equals new width; cwd inherited.
3. Run `yes` in tab 2, switch to tab 1: tab 1 responsive, tab 2 gets `◦`; switching back shows
   current output; no flicker of tab 2 content while tab 1 active.
4. `printf '\e[?1004h'; cat -v` in a tab: switching away/back prints `^[[O` / `^[[I`.
5. Resize window with 3 tabs: all tabs get SIGWINCH (`trap 'tput cols' WINCH`).
6. `exit` in active middle tab: neighbour activates; last tab exit closes window; sidebar hides at 1.
7. Compositor close with 3 tabs: all shells get SIGHUP, process/instance cleanup (no leaks under
   `foot --server`, check `/proc/<pid>/fd` count).
8. Mouse: click rows, middle-click close, `+`; pointer moves sidebar↔grid without BUG.
9. Selection and mouse reporting in the grid still map to the right cell with the sidebar shown.
10. Scale: move window between 1× and 2×/fractional outputs; sidebar edge aligned, text sharp.
11. `footclient --tab`, `footclient --workspace=CBC`, with no window open, with old server.
12. `merge-window`: tabs land in the last-focused other window; source closes; sizes correct.
13. Session: 2 windows (one with workspaces CBC (3 tabs, one split pair) and general (1 tab), one
    plain), log out/in (or restart server): workspaces, order, names, active tab per workspace,
    current workspace, splits, focused pane, placement restored.
14. Bell in hidden tab with window focused: `•`, no urgency; window unfocused: urgency.
15. Sixel image in hidden tab, then switch: renders correctly.
16. Search (`Ctrl+Shift+r`) open, then `next-tab`: search closes, no stale search box. Same with
    search or URL mode open, then the tab's shell exits: neighbour shown, no assert.
17. `yes` in a hidden tab for a minute: foot's RSS stays flat (§5.1b); no wakeups from hidden tabs'
    blink timers.
18. With 3 tabs, compositor close: no tab gets SIGWINCH during shutdown (§5.5 `closing`).
19. `Control+Shift+plus` with 2 tabs: both tabs change font size, `tput cols` equal in both.
20. `new-tab` with a nonexistent shell (`-o shell=/nope`): error, sibling tabs and window survive.
21. Visual bell (`[bell] visual=yes`) in a hidden tab: no 100% CPU (§5.1 #3).
22. Close one tab of 3, log out/in: closed tab does not come back (§8.2).
23. Integer-scale output: sidebar width positive and correct (§6.2).
24. Touch tap on a sidebar row, then move pointer off the window: no assert (§6.4).
25. Drag-resize with 3 tabs: all tabs get SIGWINCH during the drag (§5.3).
26. Session file written by unpatched 1.28.0 (v4) restores as single-tab windows.
27. `Control+Shift+plus` twice, then `new-tab`: new tab has the zoomed font size (§5.4).
28. `merge-window` with search open and a selection in the source: no stale subsurface, no assert,
    no cursor blink in the merged tabs while unfocused, no crash from the chord's key release or a
    wheel event during the merge; with both windows on one output, `dst`'s scale and font are
    unchanged and a later move to another output still rescales (§5.8).

Workspaces and rename:
29. `new-workspace` twice: switcher shows `1 2 3`, each has its own tab list and active tab;
    switching back restores the active tab; no SIGWINCH on switch.
30. 2 workspaces × 1 tab: sidebar visible; close one → its workspace drops, sidebar hides, grid widens.
31. `move-tab-to-workspace-2` with the last tab of workspace 1: workspace 1 drops, tab follows, title
    prefix updates.
32. `footclient --workspace=CBC` with CBC in a non-focused window's non-current workspace: tab lands
    there, window raised, CBC current. CBC nowhere: created in the last-focused window. No window:
    new window titled `CBC: …`.
33. foot.ini `workspace=general` and plain `footclient`: new window (no tab bit).
34. Double-click chip → type `CBC` → Enter: title `CBC: …`, chip renamed, survives restart.
35. Rename: Escape restores the old name; a duplicate keeps the field open; BackSpace/arrows/Home/End
    work; dead keys (`' e` → `é`) and an fcitx5 commit insert text; nothing reaches the pty
    (`cat -v` shows nothing).
36. Rename open, then `next-tab` / click a tab row / close the workspace's last tab: field closes, no
    stale buffer, no crash.
37. Bell in a tab of another workspace: chip `•`; cleared once that tab is shown.
38. `merge-window` from workspaces `CBC`,`1` into `CBC`,`general`: dst has `CBC` (tabs merged),
    `general`, one unnamed; sizes correct; active tab = src's.

Drag and detach:
39. Drag a row in a 4-tab window: rows follow the pointer; order persists across log out/in.
40. Press and release without moving half a row: activates only.
41. Drag a row onto the grid and release: tab opens in a new window with scrollback and program
    intact; source sidebar hides with one tab left; no `fdm_add`/`EEXIST` in the log; new window's
    workspace has the source workspace's name.
42. `detach-tab` on the active tab of 3: neighbour active in the source, new window titled
    correctly; on a 1-tab window: no-op.
43. Detach with search open and a selection in the moved tab: no stale subsurface, no assert.
44. Detach, then `merge-window` back: fonts and scale match; on mixed-scale outputs the detached
    window rescales when moved.
45. Touch-drag a row (reorder, then drag-out), then move the mouse off the window: no assert.
46. Shell exits in the dragged tab mid-drag; compositor workspace switch mid-drag: drag cancels, no
    crash, no detach.
47. Drag a row onto another workspace's chip: tab moves there and becomes current.
48. Detach, log out/in: both windows restored with their tabs.

Split view:
49. `split-new` twice: 3 panes, one sidebar row; typing goes to the focused pane; each pane's program
    sees its own `$COLUMNS`.
50. Click an unfocused pane: focus moves, the click also selects; previous pane shows the hollow cursor.
51. Drag-resize with a split visible and with a split hidden: all members get SIGWINCH to pane width;
    switching back to the hidden group does not reflow.
52. `close-tab` on the middle of 3 panes: 2 remain, widths rebalance; close one more: single tab full
    width, no stale subsurface.
53. Search and URL mode in the right pane: box/labels over that pane.
54. Move a split window between 1× and 2×: panes and background rescale, no gap artefacts.
55. `merge-window` and drag-out of a split row: group arrives intact; no assert from a pane callback
    in flight. `detach-tab` on a pane: only it moves, the rest stays split (or unsplits at 1).
56. `split-new` past the minimum width: refused with bell, no layout change.
57. Bell or output in a hidden group member: row marker; in a visible unfocused pane: none.
58. `move-tab-to-workspace-2` on a split: whole group moves, stays split.

Standalone `--tab`:
59. Standalone foot A, `foot --tab` inside it: tab opens in A; `foot --tab false; echo $?` → 1.
60. Standalone A and B, focus B, launch `foot --tab` from the launcher: tab in B.
61. `kill -9` the last-focused foot, `foot --tab`: new standalone window, no error; focusing it
    repoints the link.
62. `foot --server` + standalone A: `foot --tab` follows whichever was focused last.
63. `env -u XDG_RUNTIME_DIR foot`, then `foot --tab`: both start normally as new windows.
64. `foot --tab --server`, `foot --tab --pty=/dev/pts/N`: error, exit 1.
65. Standalone A, add a tab via `foot --tab`, exit A's first shell: window stays; process exits after
    the last tab; socket and link removed.
66. Standalone A with a client-added tab, `kill -USR1`: both tabs switch theme.
67. `foot --tab -f monospace:size=20 vim`: warning, vim opens as tab.

Activity:
68. Tab A runs `sleep 2; echo hi`, switch to B: A gets `◦` after 2 s; showing A clears it.
69. htop in a hidden tab, drag-resize the window: no activity marker.
70. vim with focus reporting in a tab, switch away: no activity marker.
71. Hidden tab prints then rings the bell: `•`; `[tabs] activity=no`: output alone shows nothing.
72. Press a non-current chip / a tab row / an unfocused pane, release: drag ends, no "stray button
    release" in the log; double-click a non-current chip enters rename.
73. Restore with 3 hidden tabs: no `◦` from shell startup.
74. Split, touch down on the unfocused pane and drag: selection in that pane; close the pane mid-touch:
    no crash.
75. `foot --tab` from fuzzel/niri spawn: target window gets focus (activation token).
76. Rename, hold Enter to commit: nothing reaches the pty.
77. niri (SSD): output in a background tab shows `◦` with no other window activity.

## 12. Tasks and dependencies

| ID | Task | Blocked by |
|----|------|-----------|
| T0 | Work tree + empty `foot-tabs.patch` wired into spec (Patch2) and meson (`tabs.c`) | — |
| T1a | Data model (§4), `tabs_is_visible` (= active until T26), `tabs_sidebar_width_px`, `wayl->windows`, `term_init(attach_to, ws, split)` (§5.4), `tabs_adopt_fonts`, `tabs_attach/detach` | T0 |
| T1b | `term_release_window`, `fdm_shutdown`/`term_destroy` rewrite, `wayl_win_destroy(win, term)` signature + purge, `closing`, `tabs_close_window`, URL token guard (§5.5) | T1a |
| T2 | Render gating (§5.1, §5.1b) and `tabs_activate` repaint/title steps (§5.2 #1-3, 5-9) | T1b |
| T3 | `tabs_layout` for unsplit tabs, sidebar margin in `render_resize`, shared resize timer, configure loop (§5.3) | T1a |
| T4 | Focus handover on switch (§5.2 #4), focus_seq | T2 |
| T5 | `tab_host` standalone + `new-tab`, next/prev/select/move/close actions + defaults (§3.3, §5.4) | T2, T3, T4, T13 |
| T6 | Sidebar subsurface + `render_sidebar` (§6.1-6.3, 6.5, 6.6) | T3 |
| T7 | Sidebar pointer input, wheel guard, touch restore fix (§6.4) | T5, T6 |
| T8 | `workspace` config key + `config_clone`/`config_free`/`value_to_str`, `--workspace` for foot (§7.4, §9) | T0 |
| T9 | Bell marker, urgency rule, notify focus (§5.6) | T4, T6 |
| T10 | Server: `tab_host` server impl (incl. `window_closing`), protocol bit, footclient `--tab`/`--workspace` (implies tab), workspace-aware `tabs_find_target` (§5.4, §7.1, §7.2, §7.4) | T5, T8, T18 |
| T11 | `tabs_transfer` + `merge-window` with workspace map, `csd_destroy` fix (§5.8, §5.9) | T4, T5, T12a, T18 |
| T12a | Session record split, track/untrack/destroy, `tab_moved`, v5 write/read with workspaces and groups (§8.1, §8.2) | T10, T18 |
| T12b | Session restore: per-tab callback, `restore_window` rework, workspaces and groups (§8.3) | T12a |
| T13 | Single-term fixes: `out:`, `wayl_destroy`, sigusr without server branch (§5.7), DnD, output removal dedupe | T1a |
| T15 | Docs, foot.ini, completions (§9) | T5, T8, T10, T11, T20, T21, T23, T28, T29, T30, T31, T32 |
| T16 | Tests + manual checklist (§11) | T7, T9, T12b, T13, T15, T19, T21, T24, T29, T30, T31, T32 |
| T17 | Spec bump, changelog, commit, COPR release | T16 |
| T18 | Workspace model: `struct tab_ws`, `term->ws`, `tabs_ws_*`, workspace-aware activate/detach/rows/move, title prefix (§4, §5.2, §5.5, §5.6, §5.11) | T5, T8 |
| T19 | Switcher row render + pointer, filtered rows, chip markers (§3.1, §6.2-6.4) | T7, T9, T18 |
| T20 | Workspace actions (`new-workspace`, next/prev/select, `move-tab-to-workspace-N`) | T18 |
| T21 | Inline rename: key/IME intercept, `rename_input`, field render, double-click (§5.12) | T19 |
| T23 | `detach-tab`: `tabs_detach_window`, `adopted` configure/shutdown handling, `session_tab_moved` (§5.10) | T11 |
| T24 | Sidebar drag: reorder, drag-out detach, chip drop, cancel paths (§6.7) | T7, T19, T23 |
| T25 | Split model + layout: `group`, `tabs_layout` panes, `RESIZE_PANE`, `tabs_win_size`, CSD geometry (§5.3, §5.13) | T3 |
| T26 | Pane surfaces + render: `term->pane`, background, `term_surf`/`term_frame_cb`/`term_pane_x`, visible gating, subsurface offsets (§5.1, §5.13) | T2, T25 |
| T27 | Pane input + focus: `tabs_term_for_surface`, `term_surface_kind`, assert relax, click-to-focus, `tabs_focus_pane`, group switch in `tabs_activate` (§5.2, §5.13) | T4, T26 |
| T28 | Split actions + group semantics of existing actions, close/workspace-move with groups (§3.3, §5.13) | T5, T18, T27 |
| T29 | Sidebar group rows + markers (§3.1, §6.3) | T19, T28 |
| T30 | Groups across merge/detach/session (§5.8, §5.10, §8) | T12b, T23, T28 |
| T31 | Standalone `--tab`: `server_init(path, embedded)`, pointer upkeep, `SO_PEERCRED`, hand-off to footclient, option checks (§7.3, §7.4) | T10, T13 |
| T32 | Activity marker: fields, `fdm_ptmx` edge, mutes, clear on show, `[tabs] activity`, glyph (§5.14, §6.3) | T6, T9 |

Critical path: T0 → T1a → T1b → T2 → T4 → T5 → T18 → T10 → T12a → T12b → T30 → T16 → T17.

## 13. Risks

- **Missed commit path** draws a hidden tab onto a surface (flicker / wrong content). Mitigation:
  grep every `wl_surface_commit(…window->surface` and `->surface.surf` in the patched tree during T2
  and T26; `xassert(tabs_is_visible(term))` in `grid_render`.
- **Dangling seat pointers** after a tab closes or moves (`kbd_focus`, `mouse_focus`, `ime_focus`) →
  UAF. Mitigation: `tabs_detach` clears all; `xassert` in `term_destroy` that no seat references `term`.
- **Desync panes vs background**: one frame of mismatch during a resize (panes at new size before
  the background). Accepted; sync subsurfaces would need a parent commit per pane frame.
- **Scope**: 32 tasks in one patch. Split (T25-T30), drag/detach (T23-T24) and standalone `--tab`
  (T31) sit off the core path and can ship in a later release if the patch gets unwieldy.
- **Session code churn** with `foot-session-restore.patch` overlap (D10).
- **Threads per tab**: each tab starts `render_worker_count` (= nproc, pixman only, `config.c:3691`)
  workers. Accepted; clamp for `attach_to` tabs if tab counts grow.
- **Version skew** server/client (§7.4).
- **Downgrade loses the session**: a v4 reader rejects a v5 file and `read_state` has already renamed
  it to `.restored`. Accepted.
- **Standalone socket per process**: one more fd and an `$XDG_RUNTIME_DIR` entry per standalone foot;
  stale sockets after SIGKILL are harmless (ECONNREFUSED → fallback) but accumulate until reboot.
