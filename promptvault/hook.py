#!/usr/bin/env python3
"""UserPromptSubmit hook: captures prompts in real-time to an append-only JSONL log.

This script is called by Claude Code on every prompt submission.
It MUST be fast (<50ms), silent (no stdout), and never fail (exit 0 always).
"""

from __future__ import annotations

import json
import os
import sys
import time


def main():
    try:
        data = json.load(sys.stdin)
        log_path = os.environ.get(
            "PROMPTVAULT_CAPTURE_LOG",
            os.path.expanduser("~/.claude/prompt-library/capture.jsonl"),
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        entry = {
            "prompt": data.get("prompt", ""),
            "session_id": data.get("session_id", ""),
            "cwd": data.get("cwd", ""),
            "timestamp": int(time.time() * 1000),
        }

        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Never block Claude Code


if __name__ == "__main__":
    main()
