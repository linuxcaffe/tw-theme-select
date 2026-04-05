- Project: https://github.com/linuxcaffe/tw-theme-select
- Issues:  https://github.com/linuxcaffe/tw-theme-select/issues

# theme-select

Three things in one: a live-preview theme browser, an interactive color editor,
and an automatic per-report theme switcher that requires no manual intervention
once configured.

## TL;DR

- Full-screen three-panel TUI: theme list | live report preview | color legend
- Navigate the list — preview updates instantly as you move
- `l` opens the color legend panel; `Tab` focuses it; `Enter` opens the color picker
- Edit any theme color interactively with a scrollable swatch reference
- `Space` or `Enter` applies the selected theme (writes to `themes.rc`, never touches `.taskrc`)
- `e` opens the selected theme file in `$EDITOR`
- Per-report themes: configure `report.list.theme=dark-green-256` in `themes.rc` and
  `tw list` automatically runs in green, then restores your default theme afterward
- `tw theme list` opens the TUI pre-set to configure the `list` report's theme
- Requires Taskwarrior 2.6.0+, Python 3.6+

## Why this exists

Taskwarrior ships with 14+ color themes. Switching between them means editing `.taskrc`,
commenting one `include` line out and uncommenting another. Comparing themes means editing,
running a report, editing again. `theme-select` collapses that to a single keypress.

The color editor goes further: select any color attribute from the live legend, edit
the fg/bg values with a scrollable 256-color swatch as reference, and see the change
reflected immediately — no manual file editing required.

The per-report switching goes further still: different reports serve different purposes.
A `ready` report for focused work, a `list` report for overview, a `minimal` report for
sharing. Each can have its own palette, applied automatically and restored cleanly.

## Installation

### Option 1 — Via [awesome-taskwarrior](https://github.com/linuxcaffe/awesome-taskwarrior)

```bash
tw -I theme-select
```

Installs both scripts to `~/.task/scripts/` and registers the per-report switcher
with `tw`. On first run, `theme-select` creates `~/.task/config/themes.rc` and
wires it into `.taskrc` automatically.

### Option 2 — Install script

```bash
curl -fsSL https://raw.githubusercontent.com/linuxcaffe/tw-theme-select/main/theme-select.install | bash
```

### Option 3 — Manual

```bash
curl -fsSL https://raw.githubusercontent.com/linuxcaffe/tw-theme-select/main/theme-select.py \
  -o ~/.task/scripts/theme-select.py
curl -fsSL https://raw.githubusercontent.com/linuxcaffe/tw-theme-select/main/theme-wrap.py \
  -o ~/.task/scripts/theme-wrap.py
chmod +x ~/.task/scripts/theme-select.py ~/.task/scripts/theme-wrap.py
```

Then register the per-report switcher manually (see [Per-report themes](#per-report-themes)).

## Usage

```bash
theme-select             # browse themes, preview against 'next' report
theme-select list        # preview against 'list', apply sets report.list.theme=
theme-select ready       # preview against your 'ready' report (or any report name)
theme-select --dir PATH  # include an extra themes directory
```

**Keys**

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate theme list (or legend when focused) |
| `j` `k` | Navigate theme list (always) |
| `Space` or `Enter` | Apply selected theme |
| `l` | Toggle color legend panel |
| `Tab` | Focus / unfocus the legend panel |
| `Enter` (legend focused) | Open color picker for selected attribute |
| `g` / `G` | Jump to top / bottom of theme list or legend |
| `e` | Open selected theme file in `$EDITOR` |
| `r` | Refresh (clears cache, re-reads themes.rc, rescans) |
| `q` or `Esc` | Quit |

**Display**

```
[ theme list  ] | [ report preview (live, full color) ] | [ color legend ]
```

The left panel lists all discovered themes; the active theme is marked `●`.
The middle panel shows a live preview of the selected theme rendered in full color
via a pseudo-terminal (task thinks it's talking to a real terminal, so colors appear
exactly as they would in normal use).
The right panel (toggle with `l`) shows `task colors legend` — every color attribute
in the theme, rendered in its own color, with its name. Navigate the legend with
arrow keys, press `Enter` to edit that attribute.

The header shows the current report and `rule.precedence.color` for the selected theme.
The legend panel requires a terminal at least ~103 columns wide.

## Color editor

Press `l` to open the legend panel, `Tab` to move focus to it, then navigate with
`↑`/`↓` to the attribute you want to change. Press `Enter` to open the picker:

- The picker shows a scrollable 256-color swatch (from `task colors`)
- Two input fields: `fg` and `bg` — `Tab` switches between them
- Type a color value (e.g. `bold white`, `color203`, `bright blue`)
- `↑`/`↓` scroll the swatch for reference
- `Enter` writes the value directly to the theme file
- `Esc` cancels

The edit is written immediately to the theme file. The preview and legend refresh
automatically to show the result. Only themes in writable locations (e.g.
`~/.task/themes/`) can be edited; system themes are read-only.

## themes.rc

On first run, `theme-select` creates `~/.task/config/themes.rc` and adds a single
`include ~/.task/config/themes.rc` line to `.taskrc` (replacing any bare theme
includes already there). After that, `.taskrc` is never touched again.

`themes.rc` is the only file `theme-select` writes to. It holds two kinds of lines:

```
# Per-report theme overrides — read by tw, ignored by task:
report.list.theme=dark-green-256
report.ready.theme=solarized-dark-256

# Theme includes — theme-select manages these:
#include /home/user/.task/themes/dark-16.theme
include /home/user/.task/themes/dark-256.theme
#include /usr/share/taskwarrior/light-256.theme
...
```

The `include` block is rewritten each time you apply a theme. The config lines above
it are preserved.

## Per-report themes

Add `report.<name>.theme=<theme-stem>` lines to `themes.rc`:

```
report.list.theme=dark-green-256
report.ready.theme=solarized-dark-256
report.minimal.theme=no-color
```

The theme stem is the filename without `.theme` (e.g. `dark-green-256` for
`dark-green-256.theme`). Themes are found in `~/.task/themes/` and
`/usr/share/taskwarrior/`.

Once configured, this happens automatically when you use `tw`:

```
tw list    →  themes.rc patched to dark-green-256  →  task list  →  themes.rc restored
tw next    →  no override configured               →  task next  (default theme unchanged)
```

The restore always happens — even if task exits with an error.

### Configuring per-report themes interactively

```bash
tw theme list    # opens TUI in configure mode for 'list'
tw theme ready   # opens TUI in configure mode for 'ready'
```

In configure mode, `Space`/`Enter` sets `report.<name>.theme=` in `themes.rc` rather
than changing the global active theme.

### How the "theme-switch" wrapper works

After `tw -I theme-select`, `~/.task/config/.tw_wrappers` contains two entries:

```
theme|theme-select.py|...|command
theme-switch|theme-wrap.py|...|pre-exec
```

`theme-switch` is a `pre-exec` wrapper — it runs automatically before every `tw`
invocation, no keyword needed. `tw` calls `theme-wrap.py` twice per run:

- **before** task executes: patches `themes.rc` if the current report has a configured theme
- **after** task exits: restores `themes.rc` from the saved original (always, even on error)

## Theme search paths

Themes are discovered in this order (first match wins for duplicate names):

1. `~/.task/themes/` — user themes
2. `/usr/share/taskwarrior/` — system themes
3. `/usr/local/share/taskwarrior/`
4. Any path passed via `--dir PATH`

## Project status

v0.3.0 — theme browser, color editor, and per-report switcher are all stable.

## Further reading

- [awesome-taskwarrior](https://github.com/linuxcaffe/awesome-taskwarrior) — the
  ecosystem this tool belongs to, including the `tw` package manager
- [Taskwarrior theme documentation](https://taskwarrior.org/docs/themes/) — the
  official theme reference

## Metadata

- License: MIT
- Language: Python 3
- Requires: Taskwarrior 2.6.0+, Python 3.6+
- Platforms: Linux
- Version: 0.3.0
