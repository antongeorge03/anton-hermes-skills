# anton-hermes-skills — a Hermes skill tap

Public skill tap for Hermes Agent (CSCI 599 Assignment 3, advanced-integration option:
custom skill published to a public GitHub repository used as a Hermes skill tap).

## Skills

| Skill | What it does |
|---|---|
| `deadline-tracker` | Track assignment/project deadlines locally; list what is due soon. Stdlib-only, no network, no environment variables. |

## Install on any Hermes

```bash
hermes skills tap add antongeorge03/anton-hermes-skills
hermes skills search deadline
hermes skills install antongeorge03/anton-hermes-skills/skills/deadline-tracker
```

Pinned version: tag `deadline-tracker-v1.0.1` (v1.0.0 = `e0366f7` was blocked by the Hermes skills-guard scan because the script read an
environment variable; v1.0.1 reads none and scans **SAFE**).

Repository: https://github.com/antongeorge03/anton-hermes-skills

## Try it

```bash
hermes chat -q "Use the deadline-tracker skill: HW4 for CSCI599 is due 2026-11-20 at 23:59. Then list what's due."
```
