#!/usr/bin/env python3
"""Poll the project, batch changes for 60s, then build, commit, and push."""
import subprocess, time
from pathlib import Path

ROOT = Path(__file__).parent
INTERVAL = 5
QUIET_SECONDS = 60

def snapshot():
    return {p.relative_to(ROOT).as_posix(): (p.stat().st_mtime_ns, p.stat().st_size) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts}

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

def sync():
    run('python3', 'build_index.py')
    run('git', 'add', '.')
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT).returncode == 0:
        return
    run('git', 'commit', '-m', 'sync daily reading feed')
    run('git', 'push', 'origin', 'main')

print('daily-signal watcher running')
last = snapshot(); changed_at = None
while True:
    time.sleep(INTERVAL)
    current = snapshot()
    if current != last:
        last = current; changed_at = time.time(); print('change detected; waiting for quiet window', flush=True)
    elif changed_at and time.time() - changed_at >= QUIET_SECONDS:
        try:
            sync(); print('synced', flush=True)
        except subprocess.CalledProcessError as exc:
            print(f'sync failed: {exc}', flush=True)
        changed_at = None
