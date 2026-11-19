---
name: deadline-tracker
description: Track assignment and project deadlines locally and list what is due soon. No accounts, no network, no credentials.
version: 1.0.1
author: Anton George
license: MIT
metadata:
  hermes:
    tags: [deadlines, school, productivity, students]
---

# Deadline tracker

Keeps a small local list of deadlines in `~/.hermes/deadline-tracker/deadlines.json`
(override with `--file PATH`). Standard-library Python only; reads no environment variables and never
contacts the network.

Run the helper with the terminal tool. Always quote arguments.

| Goal | Command |
|---|---|
| Add | `python3 ${HERMES_SKILL_DIR}/scripts/deadlines.py add "HW4" 2026-11-20T23:59 --course CSCI599` |
| List (next 14 days) | `python3 ${HERMES_SKILL_DIR}/scripts/deadlines.py list` |
| List everything incl. done | `python3 ${HERMES_SKILL_DIR}/scripts/deadlines.py list --days 365 --all` |
| Due within 3 days | `python3 ${HERMES_SKILL_DIR}/scripts/deadlines.py due-soon --days 3` |
| Mark done | `python3 ${HERMES_SKILL_DIR}/scripts/deadlines.py done <id>` |

Workflow:
1. When the user mentions a deadline ("HW4 is due Friday 11:59pm"), resolve the date in the
   user's timezone (pass `--tz <IANA zone>` before the subcommand; default America/Los_Angeles), then run `add`
   with an ISO date or date-time. Confirm the resolved date back to the user.
2. For "what's due?", run `list` and present items soonest first; flag anything due in under
   3 days and anything `overdue`.
3. To finish an item, run `list` to find its `id`, then `done <id>`.

The script prints JSON (or one line per item for `due-soon`) and exits non-zero on bad input.
It never contacts the network.
