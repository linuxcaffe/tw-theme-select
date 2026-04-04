#!/usr/bin/env python3
"""
theme-wrap — per-report theme switcher for Taskwarrior
Part of the awesome-taskwarrior suite.

Implements the tw pre-exec wrapper protocol (type=pre-exec in .tw_wrappers).
Register once in ~/.task/config/.tw_wrappers:

    theme-switch|theme-wrap.py|Per-report theme switching|pre-exec

Config lives in themes.rc alongside the include lines:

    report.list.theme=dark-green-256
    report.ready.theme=solarized-dark-256

tw calls this script twice per invocation:
  TW_PRE_EXEC_PHASE=pre  — patch themes.rc, save original
  TW_PRE_EXEC_PHASE=post — restore themes.rc from saved state

TW_REPORT holds the detected report name.
TW_PRE_EXEC_SESSION holds a unique ID for this invocation (used for state file).

Standalone mode (no TW_PRE_EXEC_PHASE): wraps task directly, for use without tw.
"""

import os
import re
import sys
import subprocess
from pathlib import Path

THEMES_RC = Path.home() / '.task' / 'config' / 'themes.rc'
THEME_SEARCH_PATHS = [
    Path.home() / '.task' / 'themes',
    Path('/usr/share/taskwarrior'),
    Path('/usr/local/share/taskwarrior'),
]


def get_report_themes():
    """Return {report_name: theme_stem} from report.*.theme= lines in themes.rc."""
    result = {}
    try:
        for line in THEMES_RC.read_text().splitlines():
            m = re.match(r'^\s*report\.(\w+)\.theme\s*=\s*(\S+)', line)
            if m:
                result[m.group(1)] = m.group(2)
    except Exception:
        pass
    return result


def find_theme_path(stem):
    """Resolve a theme stem (e.g. 'dark-green-256') to an absolute Path."""
    name = stem if stem.endswith('.theme') else f'{stem}.theme'
    for d in THEME_SEARCH_PATHS:
        p = d / name
        if p.exists():
            return p
    return None


def patch_themes_rc(theme_path):
    """Rewrite themes.rc with theme_path as the sole active include.

    Returns original file text (for restore), or None if themes.rc is absent
    or already has the right theme active (no patch needed).
    """
    try:
        original = THEMES_RC.read_text()
    except FileNotFoundError:
        return None

    lines = []
    found = False
    already_active = False
    for line in original.splitlines(keepends=True):
        m = re.match(r'\s*#?\s*include\s+(\S+\.theme)', line)
        if m:
            p = Path(m.group(1)).expanduser()
            if p.resolve() == theme_path.resolve():
                if not line.lstrip().startswith('#'):
                    already_active = True  # already the active theme — no patch needed
                lines.append(f'include {p}\n')
                found = True
            else:
                lines.append(f'#include {p}\n')
        else:
            lines.append(line)

    if already_active:
        return None  # nothing to do, nothing to restore

    if not found:
        lines.append(f'include {theme_path}\n')

    THEMES_RC.write_text(''.join(lines))
    return original


def run_pre():
    """Pre-exec phase: patch themes.rc for the requested report."""
    report  = os.environ.get('TW_REPORT', '')
    session = os.environ.get('TW_PRE_EXEC_SESSION', 'default')

    if not report:
        sys.exit(0)

    report_themes = get_report_themes()
    stem = report_themes.get(report)
    if not stem:
        sys.exit(0)

    theme_path = find_theme_path(stem)
    if not theme_path:
        sys.exit(0)

    original = patch_themes_rc(theme_path)
    if original is not None:
        Path(f'/tmp/tw-theme-wrap-{session}.state').write_text(original)

    sys.exit(0)


def run_post():
    """Post-exec phase: restore themes.rc from saved state."""
    session    = os.environ.get('TW_PRE_EXEC_SESSION', 'default')
    state_file = Path(f'/tmp/tw-theme-wrap-{session}.state')

    if state_file.exists():
        try:
            THEMES_RC.write_text(state_file.read_text())
            state_file.unlink()
        except Exception:
            pass

    sys.exit(0)


def run_standalone():
    """Standalone mode: wrap task directly (for use without tw)."""
    user_args = sys.argv[1:]

    report_themes = get_report_themes()
    report = None
    for arg in user_args:
        if not arg.startswith('-') and '=' not in arg and ':' not in arg:
            if arg in report_themes:
                report = arg
                break

    original = None
    if report:
        theme_path = find_theme_path(report_themes[report])
        if theme_path:
            original = patch_themes_rc(theme_path)

    task_bin = None
    import shutil
    task_bin = shutil.which('task') or 'task'
    try:
        result = subprocess.run(['task'] + user_args, executable=task_bin, check=False)
    finally:
        if original is not None:
            try:
                THEMES_RC.write_text(original)
            except Exception:
                pass

    sys.exit(result.returncode)


def main():
    phase = os.environ.get('TW_PRE_EXEC_PHASE')
    if phase == 'pre':
        run_pre()
    elif phase == 'post':
        run_post()
    else:
        run_standalone()


if __name__ == '__main__':
    main()
