# Instructions for the agent (Claude Code, Codex, any agent with a browser)

Goal: build the student's remaining semesters as `plan.json`, render it with `index.html`, and keep changing it as they ask.

## Inputs (ask for anything missing)
1. **Degree audit (required).** At UT Austin: IDA (utdirect.utexas.edu/apps/degree/audits). Read the newest result: every "Lacking" row, hour totals (120 total, 36 upper-division, residence), minor rules (e.g. shared-hour caps), and limits (e.g. max hours in the major).
2. **Course schedule.** The registrar's search for the next term (UT: utdirect.utexas.edu/apps/registrar/course_schedule/<ccyys>/). Read days, times, mode, instructor, and the prerequisite line on each class page.
3. **The student's own words.** Target graduation, days they want free, max hours, how many hard classes per term, interests (e.g. AI, sports), work plans.
4. Optional: minor sheets, an existing four-year plan, past schedules.
The student signs in themselves. Never type a password.

## Process
1. Turn the audit into a list of remaining requirements and hours. Count each class once; respect shared-hour caps between major and minor.
2. Rate every candidate class 1-10 for difficulty from data, not guesses:
   - grade distributions: `python3 scripts/grades.py <grades.db> "ADV" "353"` (UT: the open-source UT Registration Plus `grade_distributions.db`)
   - RateMyProfessors: `python3 scripts/rmp.py "<Last name>"` (UT Austin school id baked in; change for other schools)
   Use A-range % (A + A-) and RMP difficulty; prefer the instructor's own history over the course average.
3. Place classes into terms: prerequisites first, at most the student's hard-class limit per term, preferred days, real offering pattern (some classes run only in some terms or only MW).
4. Write `plan.json` (shape: `plan.example.json`) and open `index.html` with it pasted into "Plan data", or embed it.
5. The student drags classes; they click "Copy plan for my agent" and paste it back to you. Re-check and explain each change in plain words: name classes by course code and name, not by professor, unless two sections of one class differ.

## plan.json fields
`rules.hoursLeft` hours still needed · `rules.hard` difficulty at or above which a class counts as hard · `rules.maxHardPerTerm` · `rules.maxHours` · `classes.<id>`: `code, name, hours, diff (1-10), prereqs [ids], note, only ["Fall","Spring","Summer"]` · `terms[]`: `term, classes [ids]`, `pool: true` for "Not taking".
