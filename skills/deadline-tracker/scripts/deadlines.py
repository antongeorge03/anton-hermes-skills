#!/usr/bin/env python3
"""deadline-tracker — track assignment / project deadlines and surface what is due soon.

Standalone, standard-library only. The same file is used two ways:
  * as a module by the A3 Hermes plugin (tools deadline_add / deadline_list / deadline_done);
  * as the CLI script of the published `deadline-tracker` skill (skills-tap/), runnable on a fresh
    Hermes install:  python3 deadlines.py add "HW3" 2026-11-20T23:59 --course CSCI599

Storage: one JSON document, replaced atomically. Default path:
  $DEADLINES_FILE, else $HERMES_HOME/deadline-tracker/deadlines.json, else ~/.hermes/deadline-tracker/deadlines.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


def default_path() -> Path:
    if os.environ.get("DEADLINES_FILE"):
        return Path(os.environ["DEADLINES_FILE"])
    home = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    return home / "deadline-tracker" / "deadlines.json"


def _tz() -> ZoneInfo:
    try:
        return ZoneInfo(os.environ.get("A3_TIMEZONE") or os.environ.get("TZ") or "America/Los_Angeles")
    except Exception:
        return ZoneInfo("UTC")


def _load(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("deadlines", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


def _save(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".deadlines.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "deadlines": items}, fh, indent=1, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def parse_due(value: str, tz: Optional[ZoneInfo] = None) -> datetime:
    """Accepts ISO 8601 ('2026-11-20', '2026-11-20T23:59', with or without offset)."""
    tz = tz or _tz()
    value = value.strip()
    if " " in value and "T" not in value:
        value = value.replace(" ", "T", 1)
    dt = datetime.fromisoformat(value)
    if len(value) == 10:  # date only -> end of day
        dt = dt.replace(hour=23, minute=59)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt


def add(title: str, due: str, course: str = "", notes: str = "", path: Optional[Path] = None) -> dict:
    title = title.strip()
    if not title or len(title) > 160:
        raise ValueError("title must be 1-160 characters")
    path = path or default_path()
    dt = parse_due(due)
    items = _load(path)
    item = {"id": uuid.uuid4().hex[:6], "title": title, "due": dt.isoformat(timespec="minutes"),
            "course": course.strip()[:60], "notes": notes.strip()[:300], "done": False,
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    items.append(item)
    _save(path, items)
    return item


def mark_done(item_id: str, path: Optional[Path] = None) -> bool:
    path = path or default_path()
    items = _load(path)
    hit = False
    for it in items:
        if it["id"] == item_id:
            it["done"] = True
            hit = True
    if hit:
        _save(path, items)
    return hit


def upcoming(days: int = 14, include_done: bool = False, path: Optional[Path] = None,
             now: Optional[datetime] = None) -> list[dict]:
    tz = _tz()
    now = now or datetime.now(tz)
    horizon = now + timedelta(days=days)
    out = []
    for it in _load(path or default_path()):
        if it.get("done") and not include_done:
            continue
        due = datetime.fromisoformat(it["due"])
        if due > horizon:
            continue
        delta = due - now
        hours = delta.total_seconds() / 3600
        it = dict(it)
        it["overdue"] = hours < 0
        it["due_in"] = ("overdue" if hours < 0 else f"{int(hours)}h" if hours < 48 else f"{delta.days}d")
        it["days_left"] = delta.days if hours >= 0 else -1
        it["due_local"] = due.astimezone(tz).strftime("%a %b %d %H:%M")
        out.append(it)
    out.sort(key=lambda x: x["due"])
    return out


def _main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Track deadlines (deadline-tracker skill).")
    p.add_argument("--file", type=Path, default=None, help="storage file (default: %(default)s)")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("title"); a.add_argument("due")
    a.add_argument("--course", default=""); a.add_argument("--notes", default="")
    ls = sub.add_parser("list"); ls.add_argument("--days", type=int, default=14)
    ls.add_argument("--all", action="store_true")
    d = sub.add_parser("done"); d.add_argument("id")
    s = sub.add_parser("due-soon"); s.add_argument("--days", type=int, default=3)
    args = p.parse_args(argv)
    try:
        if args.cmd == "add":
            print(json.dumps(add(args.title, args.due, args.course, args.notes, args.file), indent=1))
        elif args.cmd == "list":
            print(json.dumps(upcoming(args.days, args.all, args.file), indent=1))
        elif args.cmd == "done":
            ok = mark_done(args.id, args.file)
            print(json.dumps({"ok": ok}))
            return 0 if ok else 1
        elif args.cmd == "due-soon":
            items = upcoming(args.days, False, args.file)
            for it in items:
                print(f"- {it['title']} ({it['course'] or 'no course'}) due {it['due_local']} [{it['due_in']}]")
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
