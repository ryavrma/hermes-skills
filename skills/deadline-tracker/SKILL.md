---
name: deadline-tracker
description: "Track assignment and project deadlines: add, list, see what is due soon or overdue, and mark them done."
version: 1.0.0
author: Riya Verma
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Deadlines, Tasks, Reminders, Productivity]
    category: productivity
---

# Deadline tracker

Keeps a list of deadlines in `deadlines.json` in the Hermes home directory and does the date arithmetic in a small script, so "due in 3 days" and "overdue" are always exact.

## Script

`scripts/deadlines.py` in this skill's folder (Python 3, standard library only). With the default layout:

```bash
DL="python3 ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/deadline-tracker/scripts/deadlines.py"
```

| Command | Use |
|---|---|
| `$DL add --title "Lab report" --due 2026-11-20 [--time 23:59] [--tag "Physics"] [--notes "..."]` | add a deadline |
| `$DL list [--all]` | open deadlines, soonest first (`--all` includes completed) |
| `$DL due-soon [--days 3]` | open deadlines due within N days, plus overdue ones |
| `$DL done ID` | mark complete |
| `$DL remove ID` | delete |

Every command prints JSON. Each deadline has `id`, `title`, `due`, `time`, `tag`, `days_left` and `status` (`pending`, `due_today`, `overdue`, `done`).

## How to use it

- **User mentions a deadline** ("my report is due Friday"): convert the day to a date (YYYY-MM-DD), run `add`, and confirm the title and date back.
- **"What's due?"**: run `list`; group by this week / later, and mention overdue items first.
- **Reminders and briefings**: run `due-soon --days 3`; for each item say the title and how many days are left ("due tomorrow", "due in 3 days", "2 days overdue").
- **Finished**: run `done ID`.

## Rules

- Use only the script's output for dates and day counts; never compute them yourself.
- If a date is ambiguous ("next Friday"), state the date you chose.
- Never delete a deadline unless the user asks; prefer `done`.
