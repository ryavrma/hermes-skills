#!/usr/bin/env python3
"""Deadline tracker: add, list, check and complete deadlines stored in a JSON file.

Storage: $DEADLINE_TRACKER_FILE, else ${HERMES_HOME:-~/.hermes}/deadlines.json.
Dates are local calendar dates (YYYY-MM-DD) with an optional HH:MM time.
Every command prints JSON.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path


def store_path() -> Path:
    override = os.environ.get("DEADLINE_TRACKER_FILE")
    if override:
        return Path(override)
    home = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes")
    return home / "deadlines.json"


def load(path: Path) -> dict:
    if not path.exists():
        return {"next_id": 1, "items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".deadlines-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def parse_due(due: str, time: str | None) -> tuple[str, str | None]:
    d = date.fromisoformat(due)
    if time:
        datetime.strptime(time, "%H:%M")
    return d.isoformat(), time


def with_status(item: dict, today: date) -> dict:
    days = (date.fromisoformat(item["due"]) - today).days
    status = "done" if item.get("done") else "overdue" if days < 0 else "due_today" if days == 0 else "pending"
    return {**item, "days_left": days, "status": status}


def add(data: dict, title: str, due: str, time: str | None = None, tag: str = "", notes: str = "") -> dict:
    title = title.strip()
    if not title:
        raise ValueError("title is required")
    due, time = parse_due(due, time)
    item = {"id": data["next_id"], "title": title, "due": due, "time": time, "tag": tag.strip(),
            "notes": notes.strip(), "done": False}
    data["next_id"] += 1
    data["items"].append(item)
    return item


def listing(data: dict, today: date, include_done: bool = False) -> list[dict]:
    items = [with_status(i, today) for i in data["items"] if include_done or not i.get("done")]
    return sorted(items, key=lambda i: (i["due"], i["time"] or "99:99"))


def due_soon(data: dict, today: date, days: int) -> list[dict]:
    return [i for i in listing(data, today) if i["days_left"] <= days]


def find(data: dict, item_id: int) -> dict:
    for i in data["items"]:
        if i["id"] == item_id:
            return i
    raise KeyError(f"no deadline with id {item_id}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="deadlines.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="add a deadline")
    a.add_argument("--title", required=True)
    a.add_argument("--due", required=True, help="YYYY-MM-DD")
    a.add_argument("--time", help="HH:MM (24h, optional)")
    a.add_argument("--tag", default="", help="course or project label")
    a.add_argument("--notes", default="")
    ls = sub.add_parser("list", help="list open deadlines (soonest first)")
    ls.add_argument("--all", action="store_true", help="include completed ones")
    ds = sub.add_parser("due-soon", help="open deadlines due within N days, plus overdue ones")
    ds.add_argument("--days", type=int, default=3)
    for name in ("done", "remove"):
        s = sub.add_parser(name, help=f"{'mark complete' if name == 'done' else 'delete'} by id")
        s.add_argument("id", type=int)
    args = p.parse_args(argv)

    path, today = store_path(), date.today()
    data = load(path)
    try:
        if args.cmd == "add":
            out = {"added": with_status(add(data, args.title, args.due, args.time, args.tag, args.notes), today)}
            save(path, data)
        elif args.cmd == "list":
            out = {"today": today.isoformat(), "deadlines": listing(data, today, args.all)}
        elif args.cmd == "due-soon":
            out = {"today": today.isoformat(), "within_days": args.days,
                   "deadlines": due_soon(data, today, args.days)}
        elif args.cmd == "done":
            find(data, args.id)["done"] = True
            save(path, data)
            out = {"done": args.id}
        else:
            data["items"].remove(find(data, args.id))
            save(path, data)
            out = {"removed": args.id}
    except (ValueError, KeyError) as e:
        print(json.dumps({"error": str(e).strip("'")}))
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
