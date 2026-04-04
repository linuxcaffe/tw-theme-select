- Project: https://github.com/linuxcaffe/tw-theme-select
- Issues:  https://github.com/linuxcaffe/tw-theme-select/issues

# theme-select

Two things in one: a live-preview theme browser for Taskwarrior, and an automatic
per-report theme switcher that requires no manual intervention once configured.

## TL;DR

- Full-screen two-panel TUI: theme list on the left, live colored report preview on the right
- Navigate the list — preview updates instantly as you move
- `Space` or `Enter` applies the selected theme (writes to `themes.rc`, never touches `.taskrc`)
- `e` opens the selected theme file in `$EDITOR`
- Per-report themes: configure `report.list.theme=dark-green-256` in `themes.rc` and
  `tw list` automatically runs in green, then restores your default theme afterward
- Requires Taskwarrior 2.6.0+, Python 3.6+

## Why this exists

Taskwarrior ships with 14+ color themes. Switching between them means editing `.taskrc`,
commenting one `include` line out and uncommenting another. Comparing themes means editing,
running a report, editing again. `theme-select` collapses that to a single keypress.

The per-report switching goes further: different reports serve different purposes. A
`ready` report for focused work, a `list` report for overview, a `minimal` report for
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
theme-select ready       # preview against your 'ready' report (or any report name)
theme-select --dir PATH  # include an extra themes directory
```

**Keys**

| Key | Action |
|-----|--------|
| `↑` `↓` or `j` `k` | Navigate theme list |
| `Space` or `Enter` | Apply selected theme |
| `e` | Open selected theme file in `$EDITOR` |
| `r` | Refresh (re-reads themes.rc and rescans directories) |
| `g` / `G` | Jump to top / bottom |
| `q` or `Esc` | Quit |

**Display**

Left panel lists all discovered themes. The active theme is marked `●`. The right
panel shows a live preview of the selected theme applied to the report, rendered in
full color via a pseudo-terminal (task thinks it's talking to a real terminal, so
colors appear exactly as they would in normal use).

The header shows the current report name and cursor position.

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

### How the "theme" keyword works

After `tw -I theme-select`, you'll see this line in `~/.task/config/.tw_wrappers`:

```
theme|theme-wrap.py|Per-report theme switching|pre-exec
```

The keyword `theme` here is a **registration label**, not a command trigger. Unlike
`command`-type wrappers (where typing `tw 42 ann` triggers the `ann` wrapper), a
`pre-exec` wrapper runs automatically before every `tw` invocation — no keyword
needed in your command.

`tw` calls `theme-wrap.py` twice per run:
- **before** task executes: patches `themes.rc` if the current report has a configured theme
- **after** task exits: restores `themes.rc` from the saved original (always, even on error)

The keyword just gives the registration a stable name so `tw remove theme-select`
can find and remove the right entry.

## Theme search paths

Themes are discovered in this order (first match wins for duplicate names):

1. `~/.task/themes/` — user themes
2. `/usr/share/taskwarrior/` — system themes
3. `/usr/local/share/taskwarrior/`
4. Any path passed via `--dir PATH`

## Project status

Early release (v0.1.0). Core functionality is stable.

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
- Version: 0.1.0
