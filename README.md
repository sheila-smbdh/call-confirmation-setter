# Call Confirmation Center

SOPs, Close setup, automations and payout tracking for SMB Deal Hunter's Call Confirmation Specialist role (Gino Binoy, since Nov 10, 2026).

- `docs/SOP.md`: the Call Confirmation Quick Guide, updated Nov 13. `docs/sop-changes-2026-11-13.md` lists what changed and why.
- `docs/DECISIONS.md`: the decisions log. Section 0 (Nov 10–13) is the newest and overrides older sections.
- `tracker/`: the nightly update for the Call Confirmation Tracker (Google Sheet) and its history in Supabase.
  - `tracker/RUNBOOK.md`: the steps the 8pm MT scheduled task follows, and what it may and may not do.
  - `tracker/pipeline/`: offline scripts the runbook calls. They read and write local files only.
  - `tracker/supabase/call_confirmation_schema.sql`: the `call_confirm_*` tables in setter-data.
  - `tracker/data/`: each run's working files. They contain lead data, so they're gitignored and never committed.

- `scorecard/`: Gino's daily scorecard, posted to #cc-gino Mon–Fri before 7am ET. `scorecard/ROUTINE.md` has the steps; `scorecard/mockup/` has the sample PNGs.

Latest handoff: `handoffs/2026-11-04-precall-confirmation/README.md` (pre-call confirmation analysis and setter-set workflow proposal).

Pre-call confirmation findings (six months, May–Oct 2026, plus the October deep-dive): `analysis/precall-confirmation/FINDINGS.md`.
