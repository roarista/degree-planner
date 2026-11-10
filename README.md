![degree-planner](assets/banner.svg)

# degree-planner

![License: MIT](https://img.shields.io/badge/license-MIT-BF5700) ![No build](https://img.shields.io/badge/build-none-333) ![Python 3](https://img.shields.io/badge/python-3.9%2B-3776AB)

Plan the rest of college with your AI agent (Claude Code, Codex, any agent with a browser). It reads your degree audit, builds a four-year plan, picks the easiest sections that fit, and hands you unique numbers with backups. You register yourself.

## Quick start
```bash
git clone https://github.com/roarista/degree-planner && cd degree-planner && claude
# then say: "help me plan my schedule"
```
The agent follows [`AGENT.md`](AGENT.md): asks for your IDA and major/minor → requirements → 4-year plan → difficulty data → exact sections + backups → one HTML page (or Docs/Slides/Sheets).

## What's inside
| File | What it does |
|---|---|
| `index.html` | drag-and-drop four-year planner, one file, no build |
| `scripts/difficulty.py` | **1–10 difficulty for a class + professor + you** (see below) |
| `scripts/grades.py` | A-range % per professor from grade distributions |
| `scripts/rmp.py` | RateMyProfessors ratings, tags and newest reviews |
| `scripts/find.py` | classes that match your interests, easiest first |
| `scripts/export.py` | plan → Markdown / CSV / Word / PowerPoint (Google Docs / Sheets / Slides) |

## How difficulty is scored
`python3 scripts/difficulty.py grade_distributions.db ECO 330T Grooms --profile me.json --info class.json`

- **Grades (55%)**: A %, A- %, full distribution → GPA, D/F rate, for this professor in this course; small samples lean toward the course-wide numbers.
- **RateMyProfessors (45%)**: difficulty from reviews of *this course* blended with *all* the professor's reviews (more class-specific reviews → more weight).
- **Format, from reviews**: test-heavy, Honorlock/proctored, exams on Canvas vs in person, async, assignment-heavy, group projects, attendance, reading, papers, curve, extra credit, tough grader.
- **Class facts** (`--info`, from the course schedule/syllabus): mode, days, time, exam count/weight/where.
- **You** (`--profile`): `{"tests":"weak","likes":["papers"],"dislikes":["group","8am","friday"]}` moves the score for you.

Grade data: the open-source `grade_distributions.db` from [UT Registration Plus](https://github.com/Longhorn-Developers/UT-Registration-Plus) (`src/assets/database/`).

## Other schools
Change the audit/schedule URLs in `AGENT.md`, `--school <RMP id>` in the scripts, and `"school": {"color","logo"}` in your plan.

## License
MIT. Not affiliated with The University of Texas at Austin or RateMyProfessors. "Hook 'em" hand drawn from scratch; no official logos.
