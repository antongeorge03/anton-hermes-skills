# anton-hermes-skills — a Hermes skill tap

Public skill tap for Hermes Agent (CSCI 599 Assignment 3, advanced-integration option:
custom skill published to a public GitHub repository used as a Hermes skill tap).

## Skills

| Skill | What it does |
|---|---|
| `deadline-tracker` | Track assignment/project deadlines locally; list what is due soon. Stdlib-only, no network. |

## Install on any Hermes

```bash
hermes skills tap add <github-user>/anton-hermes-skills
hermes skills search deadline
hermes skills install <github-user>/anton-hermes-skills/deadline-tracker
```

Pinned version: see the tag `deadline-tracker-v1.0.0` / the commit hash in the A3 submission.

## Try it

```bash
hermes chat -q "Use the deadline-tracker skill: HW4 for CSCI599 is due 2026-11-20 at 23:59. Then list what's due."
```
