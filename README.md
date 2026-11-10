# degree-planner

Plan the rest of college with your AI agent. Give it your degree audit, the course schedule, and what you want (free days, easy terms, graduate by when). It builds a drag-and-drop plan; you move classes around; it checks prerequisites, hours, and how many hard classes land in one term.

- `index.html` the planner. One file, no build, no server. Open it locally or on GitHub Pages.
- `AGENT.md` what your agent should do (paste it into Claude Code / Codex, or point the agent at it).
- `plan.example.json` the plan format.
- `scripts/grades.py`, `scripts/rmp.py` difficulty data: grade distributions and RateMyProfessors.

Built at UT Austin. Other schools: change the audit/schedule URLs in AGENT.md and the school id in `rmp.py`.

Quick start (friend's computer): `git clone <this repo> && cd degree-planner && claude` then say "help me plan my schedule". The agent follows AGENT.md: it asks for your IDA, your major/minor, then builds a 4-year plan and a registration list with unique numbers and backups.

Roadmap: MCP server so the agent reads your moves directly instead of copy/paste.
