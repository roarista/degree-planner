# Instructions for the agent (Claude Code, Codex, any agent with a browser)

Goal: take a UT Austin student from their degree audit to a four-year plan, then to an exact registration list (unique numbers plus backups) for the next semester. Work in the order below and don't skip ahead: the four-year plan decides which classes go into the semester.

The student signs in to UT themselves. **Never type a password, never click Register/Add/Submit for them.** You read; they register.

## Step 0 — Interview (ask these first, one message)
1. Their IDA: ask them to open https://utdirect.utexas.edu/apps/degree/audits/ in Chrome and run a new audit (or paste/print it to PDF).
2. Major(s) and minor/certificate: current, and any they are applying to (e.g. internal transfer to McCombs). If applying, ask the deadline and when decisions come out: you will build **two paths**.
3. Target graduation (semester + year), current classification, the next term they register for, and their registration time.
4. Constraints: max/min hours (stay ≥12 for full-time aid, housing, scholarships), free days, work, classes they refuse (e.g. "no language at UT, I'll do it online in summer"), pairs that must not share a term, summer yes/no.
5. Anything they already took or are registered for, and transfer/AP credit.

## Step 1 — Requirements
- From the IDA: every "Lacking" row, hours (120 total, 36 upper-division, 60 in residence), core, flags, major and minor sections, caps (e.g. at most 7 hours shared between major and minor; max hours in major).
- Find the minor's own requirement sheet (college website or catalog.utexas.edu) and list its courses and hours. Same for a target major.
- **Check restrictions on every class before planning it.** Many classes say "Restricted to <college> majors" on the course schedule (e.g. ACC 311, MIS 301, B A 324, STA 235 are McCombs-only; some ECO 1-hour classes are Econ majors only). Non-majors can sometimes add after the 4th class day at 5 PM — note it, don't count on it.
- Read prerequisites on each class page; a class whose prerequisite is in the same term doesn't work.

## Step 2 — Four-year plan (before any section numbers)
- Place every remaining requirement term by term until graduation: prerequisites first, at most 1–2 hard classes a term, real offering pattern (some classes run only in fall, or only in summer, or only MW).
- If the student is applying to a new major, build Path 1 (admitted) and Path 2 (not admitted), and mark the classes that count for **both** paths — those go first.
- Electives: pick the easiest that still count (Step 3 data), and mark them **swappable**. Never put a placeholder ("an upper-division ECO"): name a real class.
- Each term ≥12 hours unless the student chose otherwise.

## Step 3 — Difficulty data (never guess)
- Grade distributions: download UT Registration Plus's open-source `grade_distributions.db` (github.com/Longhorn-Developers/UT-Registration-Plus, `src/assets/database/`). Then `python3 scripts/grades.py grade_distributions.db "ECO" "330T"` → A-range % per instructor.
- RateMyProfessors: `python3 scripts/rmp.py "<Last name>" --reviews 8` → quality, difficulty, would-take-again, top tags and the newest reviews (class, grade, comment). Read the reviews: summarize workload, exam style, attendance, extra credit, and anything the student said they hate (e.g. group projects, 8 AM). Strip trailing spaces; check department so you don't match a different person with the same last name.
- No data → show "?". Never invent a number (a "1/10" on a class with no data is a lie).
- Difficulty 1–10 = mix of (100 − A-range %) and RMP difficulty; prefer the instructor's own history over the course average.

## Step 3b — Classes they'd like
Ask their interests (e.g. AI, sports, film, business, music) and what they disliked before. Then `python3 scripts/find.py grade_distributions.db "ai,sport,film" --upper` lists matching courses, highest A-range first. Keep only ones that count for a requirement or elective slot and are offered next term (check the course schedule); give each a one-line "why you'd like it" + A% + RMP.
Verdict per class: **Take / Maybe / Avoid**, with the reason (A%, RMP difficulty, review themes, fit with interests and schedule).

## Step 4 — Next semester, exact sections
Course schedule: `https://utdirect.utexas.edu/apps/registrar/course_schedule/<ccyys>/results/?ccyys=<ccyys>&search_type_main=COURSE&fos_cn=<DEPT>&course_number=<NUM>` (ccyys: year + 2 spring / 6 summer / 9 fall, e.g. 20272 = Spring 2027). Detail page: `/<ccyys>/<unique>/`.
- For every class in that term of the plan, list sections with unique number, days, time, mode, instructor, seats/waitlist, A-range %, RMP.
- **Verify days/times on the detail page** (results-table parsing has mislabeled days before). Multi-meeting classes (e.g. lecture MW + discussion F) must fit as a whole.
- Choose the easiest instructor that fits without time conflicts. Then check the whole week together.

## Step 5 — Deliverable
One HTML page (no PNGs), with:
1. **Register now**: course code + name, unique, days/time, hours, total hours.
2. **If a class doesn't work out**: per class, 1–2 backup uniques in order; say what else changes if a backup forces a swap (e.g. backup section conflicts with another class → use this other class instead).
3. **Later adds** (e.g. 4th class day after 5 PM for restricted classes) — separate section, with conditions.
4. **Second path** schedule if the student is waiting on an admission decision.
5. Four-year plan for each path, with hours per term and difficulty per class.
Name classes by course code and name, not by professor (professor only to tell sections apart).
Other formats, whatever the student prefers: `python3 scripts/export.py plan.json md|csv|docx|pptx` (Markdown for Google Docs/Notion, CSV for Sheets, .docx for Google Docs/Word, .pptx for Google Slides/PowerPoint; docx/pptx need `pip install python-docx python-pptx`). Upload to Google Drive and choose "Open with Google Docs/Slides". If your agent has a Google Drive/Docs tool, create the doc directly.
School branding: `plan.json` → `"school": {"name": "UT Austin", "color": "#BF5700", "logo": "longhorn"}`; logo can be an emoji or an image URL for other schools.
Optional: the student can add sections in the UT Registration Plus extension to see the week; the extension crosses out conflicts.

## Step 6 — Iterate
They push back ("that's six classes", "that class is restricted", "I won't get ACC 311"). Re-check against the source, fix, and say plainly what changed. Re-verify the whole schedule after every change.

## Drag-and-drop planner (optional)
`index.html` renders a plan from `plan.json` (shape: `plan.example.json`). The student drags classes, clicks "Copy plan for my agent", and pastes it back.
`plan.json` fields: `rules.hoursLeft`, `rules.hard` (difficulty that counts as hard), `rules.maxHardPerTerm`, `rules.maxHours`; `classes.<id>`: `code, name, hours, diff, prereqs [ids], note, only ["Fall","Spring","Summer"]`; `terms[]`: `term, classes [ids]`, `pool: true` for "Not taking".
