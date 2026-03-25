"""CLI search over the promptvault SQLite database."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".claude" / "prompt-library" / "prompts.db"

# ANSI colors
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def get_db(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        print(f"Error: database not found at {db_path}", file=sys.stderr)
        print("Run 'promptvault-sync' first to build the database.", file=sys.stderr)
        sys.exit(1)
    return sqlite3.connect(str(db_path))


def ts_to_str(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def truncate(text: str, max_len: int = 120) -> str:
    text = text.replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def cmd_search(args: argparse.Namespace, db_path: Path):
    """Full-text search over prompts."""
    conn = get_db(db_path)
    query = args.query
    limit = args.limit or 20

    sql = """
        SELECT p.prompt_text, p.timestamp, p.project, c.name, c.md_path,
               bm25(prompts_fts) AS rank
        FROM prompts_fts
        JOIN prompts p ON prompts_fts.rowid = p.id
        JOIN conversations c ON p.session_id = c.session_id
        WHERE prompts_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, (query, limit)).fetchall()
    except sqlite3.OperationalError as e:
        print(f"Search error: {e}", file=sys.stderr)
        print("Tip: use simple keywords or FTS5 syntax (e.g., 'word1 word2')", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print(f"No results for '{query}'")
        return

    print(f"\n{BOLD}Found {len(rows)} result(s) for '{query}':{RESET}\n")
    for prompt_text, ts, project, conv_name, md_path, _rank in rows:
        project_short = Path(project).name if project else "~"
        print(f"  {CYAN}{ts_to_str(ts)}{RESET}  {BOLD}{truncate(prompt_text)}{RESET}")
        print(f"  {DIM}{conv_name} | {project_short} | {md_path}{RESET}")
        print()


def cmd_recent(args: argparse.Namespace, db_path: Path):
    """Show most recent prompts."""
    conn = get_db(db_path)
    limit = args.count or 10

    rows = conn.execute(
        """
        SELECT p.prompt_text, p.timestamp, p.project, c.name, c.md_path
        FROM prompts p
        JOIN conversations c ON p.session_id = c.session_id
        ORDER BY p.timestamp DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    print(f"\n{BOLD}Last {len(rows)} prompts:{RESET}\n")
    for prompt_text, ts, project, conv_name, md_path in rows:
        project_short = Path(project).name if project else "~"
        print(f"  {CYAN}{ts_to_str(ts)}{RESET}  {BOLD}{truncate(prompt_text)}{RESET}")
        print(f"  {DIM}{conv_name} | {project_short} | {md_path}{RESET}")
        print()


def cmd_list(args: argparse.Namespace, db_path: Path):
    """List conversations, optionally filtered by date or project."""
    conn = get_db(db_path)

    sql = "SELECT session_id, name, project, start_ts, end_ts, prompt_count, md_path FROM conversations"
    params: list = []
    conditions: list[str] = []

    if args.date:
        # Filter by date (YYYY-MM-DD)
        try:
            dt = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
        start_of_day = int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        end_of_day = start_of_day + 86400000
        conditions.append("start_ts >= ? AND start_ts < ?")
        params.extend([start_of_day, end_of_day])

    if args.project:
        conditions.append("project LIKE ?")
        params.append(f"%{args.project}%")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY start_ts DESC"

    if args.limit:
        sql += " LIMIT ?"
        params.append(args.limit)

    rows = conn.execute(sql, params).fetchall()

    if not rows:
        print("No conversations found.")
        return

    print(f"\n{BOLD}{len(rows)} conversation(s):{RESET}\n")
    for _sid, name, project, start_ts, end_ts, prompt_count, md_path in rows:
        project_short = Path(project).name if project else "~"
        start = ts_to_str(start_ts)
        end_time = datetime.fromtimestamp(end_ts / 1000, tz=timezone.utc).strftime("%H:%M")
        print(
            f"  {CYAN}{start}-{end_time}{RESET}  "
            f"{BOLD}{name}{RESET}  "
            f"{GREEN}{prompt_count}p{RESET}  "
            f"{DIM}{project_short}{RESET}"
        )
        if md_path:
            print(f"  {DIM}{md_path}{RESET}")
        print()


def cmd_stats(args: argparse.Namespace, db_path: Path):
    """Show vault statistics."""
    conn = get_db(db_path)

    conv_count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    prompt_count = conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    project_count = conn.execute("SELECT COUNT(DISTINCT project) FROM conversations").fetchone()[0]

    first_ts = conn.execute("SELECT MIN(start_ts) FROM conversations").fetchone()[0]
    last_ts = conn.execute("SELECT MAX(end_ts) FROM conversations").fetchone()[0]

    # Top 5 projects by conversation count
    top_projects = conn.execute(
        """
        SELECT project, COUNT(*) as cnt
        FROM conversations
        GROUP BY project
        ORDER BY cnt DESC
        LIMIT 5
        """
    ).fetchall()

    print(f"\n{BOLD}Prompt Vault Stats{RESET}\n")
    print(f"  Conversations:  {CYAN}{conv_count}{RESET}")
    print(f"  Prompts:        {CYAN}{prompt_count}{RESET}")
    print(f"  Projects:       {CYAN}{project_count}{RESET}")
    if first_ts and last_ts:
        print(f"  Date range:     {CYAN}{ts_to_str(first_ts)} — {ts_to_str(last_ts)}{RESET}")

    if top_projects:
        print(f"\n  {BOLD}Top projects:{RESET}")
        for project, cnt in top_projects:
            project_short = Path(project).name if project else "~"
            bar = YELLOW + "█" * min(cnt, 40) + RESET
            print(f"    {project_short:30s} {bar} {cnt}")

    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="promptvault",
        description="Search your Claude Code prompt history",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to prompts.db (default: ~/.claude/prompt-library/prompts.db)",
    )

    subparsers = parser.add_subparsers(dest="command")

    # search
    search_p = subparsers.add_parser("search", help="Full-text search prompts")
    search_p.add_argument("query", help="Search query (FTS5 syntax)")
    search_p.add_argument("-n", "--limit", type=int, default=20, help="Max results")

    # recent
    recent_p = subparsers.add_parser("recent", help="Show recent prompts")
    recent_p.add_argument("count", nargs="?", type=int, default=10, help="Number of prompts")

    # list
    list_p = subparsers.add_parser("list", help="List conversations")
    list_p.add_argument("--date", help="Filter by date (YYYY-MM-DD)")
    list_p.add_argument("--project", help="Filter by project name (partial match)")
    list_p.add_argument("-n", "--limit", type=int, help="Max results")

    # stats
    subparsers.add_parser("stats", help="Show vault statistics")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    db_path = args.db or Path(os.environ.get("PROMPTVAULT_DB", str(DEFAULT_DB_PATH)))

    commands = {
        "search": cmd_search,
        "recent": cmd_recent,
        "list": cmd_list,
        "stats": cmd_stats,
    }

    if args.command in commands:
        commands[args.command](args, db_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
