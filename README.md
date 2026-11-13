# hermes-skills

A Hermes Agent skill tap.

## Skills

| Skill | What it does |
|---|---|
| `deadline-tracker` | Tracks deadlines in a JSON file in the Hermes home directory: add, list, due soon, overdue, done. Python 3 standard library only. |

## Install

```bash
hermes skills tap add ryavrma/hermes-skills
hermes skills inspect ryavrma/hermes-skills/skills/deadline-tracker
hermes skills install ryavrma/hermes-skills/skills/deadline-tracker --category productivity
```

Tested with Hermes Agent v0.22.7.
