"""Visual testing tool for promptvault's fzf interface.

Uses `expect` to drive fzf in a real pseudo-terminal and captures the
screen buffer content. This gives an accurate representation of what the
user sees.

Usage:
    python tests/visual_test.py                    # Default view, capture after 2s
    python tests/visual_test.py --keys ctrl-t      # Send ctrl-t and capture
    python tests/visual_test.py --keys tab tab      # Send two tabs
    python tests/visual_test.py --query pytest      # Start with query
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

# Key code map for expect send syntax
EXPECT_KEY_MAP = {
    "ctrl-t": r"\x14",
    "ctrl-p": r"\x10",
    "ctrl-d": r"\x04",
    "ctrl-g": r"\x07",
    "ctrl-b": r"\x02",
    "ctrl-o": r"\x0f",
    "ctrl-x": r"\x18",
    "ctrl-y": r"\x19",
    "ctrl-e": r"\x05",
    "ctrl-/": r"\x1f",
    "tab": r"\t",
    "btab": r"\x1b\[Z",
    "enter": r"\r",
    "esc": r"\x1b",
    "up": r"\x1b\[A",
    "down": r"\x1b\[B",
    "alt-r": r"\x1br",
}


def build_expect_script(
    query: str | None = None,
    keys: list[str] | None = None,
    wait_ms: int = 2000,
    cols: int = 140,
    rows: int = 45,
    capture_file: str = "/tmp/pv_screen.txt",
) -> str:
    """Build an expect script that launches pv, sends keys, and captures screen."""
    pv_cmd = f"{sys.executable} -m promptvault.search"
    if query:
        pv_cmd += f" search {query}"

    send_cmds = ""
    if keys:
        for key in keys:
            code = EXPECT_KEY_MAP.get(key, key)
            send_cmds += f'sleep 0.5\nsend "{code}"\n'

    return f'''#!/usr/bin/expect -f
set timeout 10
set env(TERM) xterm-256color
set env(LINES) {rows}
set env(COLUMNS) {cols}

# Start in a sized terminal
proc stty_init {{}} {{}}
set stty_init "rows {rows} cols {cols}"

spawn -noecho bash -c "{pv_cmd}"

# Wait for fzf to render
sleep [expr {{{wait_ms} / 1000.0}}]

{send_cmds}

# Wait for screen to settle after keys
sleep 1

# Send escape to quit
send "\\x1b"
sleep 0.3

# Capture exit
expect eof
'''


def capture_screen_via_script(
    query: str | None = None,
    keys: list[str] | None = None,
    wait_ms: int = 2000,
    cols: int = 140,
    rows: int = 45,
) -> str:
    """Use macOS `script` command to record terminal session, then parse it."""
    pv_cmd = f"{sys.executable} -m promptvault.search"
    if query:
        pv_cmd += f" search {query}"

    # Build the key sequence to send via a helper script
    key_sequence = ""
    if keys:
        for key in keys:
            code = EXPECT_KEY_MAP.get(key, key)
            key_sequence += f"printf '{code}'\nsleep 0.5\n"

    # Create a shell script that:
    # 1. Launches pv in background
    # 2. Waits, sends keys, waits, sends ESC
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write(f"""#!/bin/bash
export TERM=xterm-256color
export LINES={rows}
export COLUMNS={cols}
stty rows {rows} cols {cols} 2>/dev/null

{pv_cmd} &
PV_PID=$!

sleep {wait_ms / 1000.0}

{key_sequence}

sleep 1

# Send ESC to quit
kill -TERM $PV_PID 2>/dev/null
wait $PV_PID 2>/dev/null
""")
        script_path = f.name

    os.chmod(script_path, 0o755)

    output_file = "/tmp/pv_visual_output.txt"

    # Use `script` to record
    result = subprocess.run(
        ["script", "-q", output_file, "bash", script_path],
        capture_output=True,
        text=True,
        timeout=wait_ms // 1000 + 10,
        env={**os.environ, "TERM": "xterm-256color", "LINES": str(rows), "COLUMNS": str(cols)},
    )

    os.unlink(script_path)

    if os.path.exists(output_file):
        with open(output_file) as f:
            return f.read()
    return result.stdout


def capture_via_expect(
    query: str | None = None,
    keys: list[str] | None = None,
    wait_ms: int = 2000,
    cols: int = 140,
    rows: int = 45,
) -> str:
    """Use expect to drive fzf and capture output via script recording."""
    expect_script = build_expect_script(query, keys, wait_ms, cols, rows)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".exp", delete=False) as f:
        f.write(expect_script)
        expect_path = f.name

    os.chmod(expect_path, 0o755)

    typescript_file = "/tmp/pv_typescript.txt"

    # Run expect under `script` to capture full terminal output
    try:
        subprocess.run(
            ["script", "-q", typescript_file, "expect", expect_path],
            capture_output=True,
            text=True,
            timeout=wait_ms // 1000 + 15,
            env={
                **os.environ,
                "TERM": "xterm-256color",
                "LINES": str(rows),
                "COLUMNS": str(cols),
            },
        )
    except subprocess.TimeoutExpired:
        pass
    finally:
        os.unlink(expect_path)

    if os.path.exists(typescript_file):
        with open(typescript_file) as f:
            raw = f.read()
        os.unlink(typescript_file)
        return raw
    return ""


def parse_screen(raw: str, rows: int = 45, cols: int = 140) -> str:
    """Parse raw script output into readable lines, stripping most ANSI codes."""
    import re

    # Strip ANSI escape sequences
    clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw)
    clean = re.sub(r"\x1b\].*?\x07", "", clean)  # OSC sequences
    clean = re.sub(r"\x1b[()][012AB]", "", clean)  # character set
    clean = re.sub(r"\x1b=", "", clean)  # DECKPAM
    clean = re.sub(r"\x1b>", "", clean)  # DECKPNM
    clean = re.sub(r"\x1b\[?[0-9;]*[hlm]", "", clean)  # modes
    clean = clean.replace("\r\n", "\n").replace("\r", "\n")

    lines = clean.split("\n")
    # Filter out empty lines and take meaningful content
    meaningful = []
    for line in lines:
        stripped = line.rstrip()
        if stripped:
            meaningful.append(stripped[:cols])

    return "\n".join(meaningful[-rows:])


def main():
    parser = argparse.ArgumentParser(description="Visual test tool for promptvault fzf UI")
    parser.add_argument("--query", help="Search query to start with")
    parser.add_argument("--keys", nargs="+", help="Keys to send (e.g., ctrl-t tab)")
    parser.add_argument("--wait", type=int, default=2000, help="Ms to wait before keys")
    parser.add_argument("--raw", action="store_true", help="Show raw output")
    parser.add_argument("--rows", type=int, default=45, help="Terminal rows")
    parser.add_argument("--cols", type=int, default=140, help="Terminal cols")
    args = parser.parse_args()

    print(f"Launching pv (wait={args.wait}ms, keys={args.keys})...", file=sys.stderr)
    raw = capture_via_expect(
        query=args.query,
        keys=args.keys,
        wait_ms=args.wait,
        cols=args.cols,
        rows=args.rows,
    )

    if args.raw:
        print(repr(raw[:5000]))
    else:
        screen = parse_screen(raw, rows=args.rows, cols=args.cols)
        print(screen)

    # Save for inspection
    out_path = "/tmp/pv_visual_test.txt"
    with open(out_path, "w") as f:
        f.write(parse_screen(raw, rows=args.rows, cols=args.cols))
    print(f"\nSaved to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
