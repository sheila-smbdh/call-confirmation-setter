# Call Confirmation Center

SOPs, Close setup, automations and payout tracking for SMB Deal Hunter's Call Confirmation Specialist role (Gino Binoy, since Nov 10, 2026).

- `docs/SOP.md`: the Call Confirmation Quick Guide, last updated Nov 19 (daily follow-up calls, next-day bookings). `docs/sop-changes-2026-11-13.md` lists what changed on Nov 13 and why.
- `docs/DECISIONS.md`: the decisions log. The newest section is first (00000, Nov 19) and overrides older ones.
- `tracker/`: the daily update (5:41am ET) for the Call Confirmation Tracker (Google Sheet) and its history in Supabase.
  - `tracker/RUNBOOK.md`: the steps the 5:41am ET scheduled task follows, and what it may and may not do.
  - `tracker/pipeline/`: offline scripts the runbook calls. They read and write local files only.
  - `tracker/supabase/call_confirmation_schema.sql`: the `call_confirm_*` tables in setter-data.
  - `tracker/data/`: each run's working files. They contain lead data, so they're gitignored and never committed.

- `precheck/`: Gino's afternoon pre-check, posted to #cc-gino Mon–Fri by 5:30pm MT (30 minutes before his shift ends): what would show as a miss on the next scorecard, while he can still fix it. `precheck/ROUTINE.md` has the steps.
- `scorecard/`: Gino's daily scorecard, posted to #cc-gino Mon–Fri before 7am ET. `scorecard/ROUTINE.md` has the steps; `scorecard/mockup/` has the sample PNGs.

Latest handoff: `handoffs/2026-11-04-precall-confirmation/README.md` (pre-call confirmation analysis and setter-set workflow proposal).

Pre-call confirmation findings (six months, May–Oct 2026, plus the October deep-dive): `analysis/precall-confirmation/FINDINGS.md`.
