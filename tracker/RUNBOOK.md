# Nightly update: Call Confirmation Tracker (Gino)

Runs every day at 8:00pm Mountain (two hours after Gino's 6pm MT shift ends), as a scheduled session.
It refreshes the tracker: https://docs.google.com/spreadsheets/d/1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk/edit

## What this run may and may not do (Sheila's standing approval, Nov 13, 2026)

May, without asking:
- Read Close (REST API, inline `curl`, one request per command), Calendly, Slack and the tracker.
- Write to the tracker: replace the Calls, Daily, Weekly, Definitions and Data Sources tabs; append new rows to
  Reviews (columns A-G and L); write Management!K5 (run time) and Management!M5 (data through).
- Reviews H-J, only where Sheila or Jay already approved the item in #cc-gino (`slack_match.py` decides), and only on
  rows whose H, I and J are all blank: H = "Excused", I = "Approved in #cc-gino: <summary> <link>", J = "<name> (Slack)".
- Supabase setter-data (ref `suoblmuvrmyfmuvlhqce`), `call_confirm_` tables only: insert or update (upsert) through
  `https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/<table>`, one inline curl per file (step 12). Never delete, never
  touch any other table, never send DDL.
- Upload one staging .xlsx to Google Drive per run (title starts with `TEMP - tracker nightly`).
- On Sundays only: post the weekly review reminder in #cc-gino (see step 13).

Must not:
- Write anything to Close, Calendly or Supabase. Never delete or merge anything in Close.
- Touch Reviews column K (the Action formula), any Reviews H-J that already has something in it, or any Management
  cell other than K5 and M5 (approvals, recovered calls, inputs).
- Post anything else to Slack, or message anyone.
- If a step fails, stop before swapping tabs. Leave the tracker as it was (Management!A5 will show STALE). Do not retry
  writes blindly: re-read the tracker first to see what already happened.

Follow `/root/.claude/CLAUDE.md` (Close and Supabase rules). Close calls are inline `curl` only, one per command, never
from a script. The scripts in `tracker/pipeline/` are offline: they only read and write local files.

## Fixed IDs

| What | Value |
|---|---|
| Tracker spreadsheet | `1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk` (sheet time zone: America/Los_Angeles) |
| Gino's Close user | `user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo` |
| Calendly organization | `https://api.calendly.com/organizations/a2c22cc2-7dde-4e50-bb22-4d5fc629e421` |
| Direct discovery event type | ends with `3de6762f19f4` (filtered in scope.py) |
| #call-confirmation (Zapier alerts) | `C0CF5TGANMT` |
| #closer-eod (Nero EOD posts) | `C06RE8S1L4V` |
| #cc-gino (Sunday reminder; Gino's exception requests) | `C0CG28G7TQT` |
| Supabase setter-data | ref `suoblmuvrmyfmuvlhqce`, tables `public.call_confirm_*` (`tracker/supabase/call_confirmation_schema.sql`) |
| Sheila / Jay (Slack) | `U0BM6J8KM32` / `U06Q63DTS13` |

Google Sheets edits go through Composio (`googlesheets` toolkit, account `googlesheets_gyte-urlar`); Drive uploads and
downloads through the Google Drive connector.

## Steps

Set `TODAY` = today's date in US Eastern (YYYY-MM-DD) and `DIR=tracker/data/$TODAY` (gitignored; never commit it).
`P=tracker/pipeline`. Dates below: `T-4` = TODAY minus 4 days, etc.

1. **Close: users and meetings**
   - `curl -s -u "$CLOSE_API_KEY:" "https://api.close.com/api/v1/user/?_limit=200" -o $DIR/users.json`
   - `python3 -I $P/bodies.py meetings $DIR $TODAY`, then one curl per body:
     `curl -s -u "$CLOSE_API_KEY:" -X POST "https://api.close.com/api/v1/data/search/" -H "Content-Type: application/json" -d @$DIR/body_meet_created.json -o $DIR/meet_created.json`
     (same for `body_meet_starts.json` -> `meet_starts.json`).
   - After each: `python3 -I $P/bodies.py check RESULT`. If TRUNCATED: delete the result, `bodies.py split BODY`, and
     pull both halves (`..._a.json`, `..._b.json`, saving results as `meet_starts_a.json` etc.; every result file name
     must start with `meet_`).

2. **Close: Gino's activity since T-4 (05:00 UTC)**
   - Calls: `.../activity/call/?user_id=GINO&date_created__gt=<T-4>T05:00:00&_limit=100&_skip=N` -> `g_call_<k>.json`;
     repeat with `_skip` +100 while `has_more` is true.
   - Texts: same with `/activity/sms/` -> `g_sms_<k>.json`.
   - Call Confirmation field history: `.../event/?user_id=GINO&object_type=lead&action=updated&date_updated__gte=<T-4>T05:00:00Z&_limit=50`
     -> `g_ev_<k>.json`; repeat with `&_cursor=<cursor_next>` until `cursor_next` is null.

3. **Calendly events** starting from T-3 to T+14:
   `mcp__Calendly__meetings-list_events` with organization above, `min_start_time` = T-3 05:00Z,
   `max_start_time` = T+14 05:00Z, `count` 100, `sort` `start_time:asc`, paging with `page_token`. Each result is
   saved to a file by the harness: copy it to `$DIR/cal_pNN.json` and run
   `python3 -I $P/calx.py $DIR/cal_events.jsonl $DIR/cal_pNN.json` (prints the next page token). A subagent can do
   the paging; pages depend on each other, so run them in order.

4. **Slack** (a subagent keeps this out of your context):
   - #call-confirmation from T-4 00:00 ET to now -> `$DIR/slack_alerts.jsonl`, one line per alert:
     `posted_at_et` ("YYYY-MM-DD HH:MM" ET), `ts`, `type` ("NEW CALL BOOKED" / "NO SHOW" / "RESCHEDULE REQUEST"),
     `lead_name`, `lead_email`, `call_datetime_text`, `lead_id` (full id from the Close link).
   - #closer-eod EOD reports dated T-3 to TODAY (read thread replies for corrections) -> `$DIR/eod_recent.json`:
     `{"YYYY-MM-DD|lead_FULLID": ["Showed" | "No-show" | "Cancelled" | "Rescheduled" | "Needs confirmation" | "Follow-up", "Closer name"]}`.
     Never guess attendance; unresolved = "Needs confirmation".

4b. **#cc-gino: exceptions Sheila or Jay already approved** (a subagent keeps this out of your context)
   - Read where the last scan stopped:
     `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_sync_state?source=eq.slack_cc_gino&select=*"`
   - If there is no row, or `full_scans` < 2: read the WHOLE channel history. Otherwise read from `last_ts` on, AND
     re-read every thread whose parent was posted in the 14 days before `last_ts` (approvals often come as thread
     replies to an older post, and those don't show up in channel history after `last_ts`).
   - Write every message and thread reply read to `$DIR/cc_gino_messages.jsonl` (`ts, thread_ts, user_id, user_name,
     posted_at_et, text, reply_count`).
   - Load the approvals already stored:
     `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_slack_approvals?select=*&limit=5000" -o $DIR/approvals_prev.json`
   - From the new messages, list each case where Gino (or anyone) raised an exception or asked what he may do, and
     Sheila (`U0BM6J8KM32`) or Jay (`U06Q63DTS13`) answered. Merge with `approvals_prev.json` (same `raised_ts` = same
     case; the newer reading wins) into `$DIR/cc_gino_approvals.json`, a list of `{raised_ts, thread_ts, raised_by,
     raised_at_et, lead_names, lead_ids, call_date_mentioned, what_gino_asked_or_reported, decision ("approved" |
     "denied" | "unclear" | "no response"), decided_by ("Sheila"/"Jay"), decision_ts, scope ("this lead only" |
     "general rule going forward"), decision_summary}`. Only Sheila's or Jay's own words count as approval; never infer
     one. If unsure, use "unclear" (it then goes to review as usual).
   - Gino often shows the lead only in a screenshot. For a lead-specific case with no name, find the lead from Gino's
     Close activity right around the post or the answer (e.g. the Call Confirmation field he set minutes after
     Sheila's reply, `g_ev_*.json`) and record how in `lead_identified_by`. If it isn't clear, leave the names empty
     (the case then matches nothing and the item goes to review as usual).
   - Note the newest `ts` read; step 12 saves it.

5. **Scope and invitees**
   - `python3 -I $P/scope.py $DIR $TODAY` -> `scope.json`, `need_invitees.txt`.
   - For every URI in `need_invitees.txt`: `mcp__Calendly__meetings-list_event_invitees` (no status filter), append one
     line per invitee to `$DIR/cal_invitees.jsonl` with `event_uri, name, email, timezone, status, created_at,
     rescheduled, old_invitee, new_invitee, cancellation` (a subagent is fine).

6. **Close: status history and calendar responses for those leads**
   - `python3 -I $P/bodies.py leads $DIR $TODAY` -> `body_lsc.json`, `body_acc.json`.
   - Pull each with the search curl -> `lsc_1.json`, `acc_1.json` (file names must start with `lsc_` / `acc_`);
     check, split and re-pull if TRUNCATED.

7. **Build**: `python3 -I $P/build.py $DIR $TODAY` -> `calls_new.json`.
   - For any row whose `check` is "Logging error: invite not accepted when he logged it (check the call transcript)",
     read Gino's call transcript (`curl -s -u "$CLOSE_API_KEY:" ".../activity/call/<id>/?_fields=id,duration,recording_transcript"`
     for the ids in the row's `transcript_calls`). If the prospect confirmed and had a technical problem accepting, add
     to `$DIR/overrides.json` `{"<lead_id>": "Valid (verbal + tech issue): <one-sentence reason>"}`; if not,
     `{"<lead_id>": "Logging error: <one-sentence reason>"}`. Re-run build.py. Don't quote transcripts at length.

8. **Merge with the live tracker**
   - `mcp__Google_Drive__download_file_content` with fileId = tracker id, exportMimeType
     `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`. The file is saved by the harness; copy it to
     `$DIR/tracker_live.xlsx`.
   - `python3 -I $P/merge.py $DIR $DIR/tracker_live.xlsx` -> `calls_all.json`, `review_keys.json`, `reviews_last_row.txt`.
   - `python3 -I $P/export.py $DIR $DIR/tracker_out.xlsx $TODAY`
   - `python3 -I $P/slack_match.py $DIR $DIR/tracker_live.xlsx` -> `slack_decisions.json`, `reviews_fill.json`.
   - `python3 -I $P/reviews.py $DIR` -> `reviews_append.json` (rows Sheila or Jay already approved in Slack come
     pre-decided).
   - General rules (approvals with scope "general rule going forward") are hints only (Sheila, Nov 13): read the new
     rows in `reviews_append.json`; for any that a general rule plausibly covers, write `$DIR/rule_hints.json`
     `{"<review key>": "Possibly covered by #cc-gino rule: <rule in a few words> <link>"}` and run reviews.py again.
     The hint goes in the note (G); the decision stays blank for Sheila and Jay.

9. **Upload the new tabs**: `sha256sum $DIR/tracker_out.xlsx`, then `mcp__Google_Drive__create_file` with title
   `TEMP - tracker nightly <TODAY> (safe to delete)`, contentMimeType
   `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, base64Content
   `sha256:<hash>:<absolute path>`. Get its sheet ids with `GOOGLESHEETS_GET_SPREADSHEET_INFO`
   (fields `sheets.properties(sheetId,title)`).

10. **Swap tabs in the tracker** (Composio). Get the tracker's current sheet ids first. Do these strictly in order,
    one tab at a time: **Calls, Daily, Weekly, Definitions, Data Sources** (Daily's formulas bind to the Calls tab that
    exists when Daily is copied in, and Weekly's to Daily):
    1. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES`: rename the current tab to `<name> (old)`.
    2. `GOOGLESHEETS_SPREADSHEETS_SHEETS_COPY_TO`: copy the tab from the TEMP file into the tracker.
    3. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES`: rename the copy (`Copy of <name>`) to `<name>`.
    After all five: `GOOGLESHEETS_DELETE_SHEET` each `<name> (old)` tab created by THIS run (only those five; match
    by the sheet ids you renamed, never by title alone; leave every other hidden or "old ..." tab alone), then set
    indexes so the order is Management (0), Reviews (1), Call Confirmation>> (2), Calls (3), Daily (4), Weekly (5),
    Call Recovery (6), Definitions (7), Data Sources (8). "Call Confirmation>>" and "Call Recovery" are Sheila's tabs:
    never edit, rename or delete them. Management uses INDIRECT for Calls and Daily, so it keeps working through the
    swap.
    Google Sheets allows about 60 reads per minute. If a call returns 429 (quota), wait 60 seconds and retry that
    one call; it did not go through.

11. **Append Reviews and stamp the time**
    - If `reviews_append.json` is non-empty: `GOOGLESHEETS_UPDATE_VALUES_BATCH` with `valueInputOption`
      `USER_ENTERED` and `data` = that file's list. (A-G and L; H-J only for rows already approved in Slack.)
    - If `reviews_fill.json` is non-empty: same call with that list (fills H-J on older blank rows that a Slack
      approval covers). Re-check first with `GOOGLESHEETS_BATCH_GET` that each of those H:J ranges is still blank;
      drop any that isn't.
    - `GOOGLESHEETS_UPDATE_VALUES_BATCH`: `Management!K5` = now in Pacific time as `YYYY-MM-DD HH:MM`, and
      `Management!M5` = TODAY.
    - Verify with `GOOGLESHEETS_BATCH_GET` of `Management!A1:A5`, `Management!A15:O16` and the last two rows of
      `Daily`: no `#REF!`, `#N/A`, `#ERROR!` or `#VALUE!`; A5 starts with "Up to date". If not, report it (step 14).

12. **Save everything to Supabase** (setter-data, `call_confirm_` tables). `RUN_ID` = the run's start time, e.g.
    `2026-11-13T20:00-07:00`.
    - Download the tracker again (as in step 8) to `$DIR/tracker_after.xlsx`, so the values saved are what the sheet
      shows after this run (Daily, Weekly, Management and Reviews, including Sheila's and Jay's decisions).
    - `python3 -I $P/supa.py $DIR $RUN_ID $DIR/tracker_after.xlsx` -> `$DIR/supa/manifest.tsv` and upload files.
    - For each manifest line `<table> <on_conflict> <file>`, one curl (no loops, no scripts):
      `curl -s -o /dev/null -w "%{http_code}\n" -X POST "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/<table>?on_conflict=<on_conflict>" -H "Content-Type: application/json" -H "Prefer: resolution=merge-duplicates,return=minimal" -d @<file>`
      Expect 201 (or 200/204). An upsert is safe to repeat, so a failed file can be sent again once.
    - Save where the #cc-gino scan stopped (one curl; `full_scans` + 1 only if this run read the whole history):
      `curl -s -o /dev/null -w "%{http_code}\n" -X POST "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_sync_state?on_conflict=source" -H "Content-Type: application/json" -H "Prefer: resolution=merge-duplicates,return=minimal" -d '{"source":"slack_cc_gino","last_ts":"<newest ts>","full_scans":<n>,"last_run_id":"<RUN_ID>"}'`
    - Last, the run record (status ok/partial/failed and a short summary of counts and warnings) in `call_confirm_runs`, same form.
    - If Supabase fails, still finish the run (the tracker is already updated); say so in the summary.

13. **Sundays only (TODAY is a Sunday in ET): weekly reminder in #cc-gino** (`C0CG28G7TQT`), after step 12:
    read `Management!A1:A4` and the row for the week that ends today, then post one message:
    ```
    <@U0BM6J8KM32> <@U06Q63DTS13> Weekly call confirmation review, week of <Mon date>–<Sun date>.
    • Compliant: <Yes/No/WAITING> (KPI 1 confirmation <x%> · KPI 2 speed to lead <y%> · KPI 3 logging <met/not met>)
    • Reviews to decide: <n> (Reviews tab, rows <list>)  — or "none"
    • Please each approve the week on the Management tab (cells D<row> and E<row>) once reviews are decided.
    Tracker: https://docs.google.com/spreadsheets/d/1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk/edit
    ```
    Use the numbers exactly as the tracker shows them. No other Slack posts.

14. **Finish**: print a short run summary (rows rebuilt, new Reviews rows, any warnings). Leave the TEMP file in Drive
    (Sheila deletes it; nothing in Drive is deleted by this run). Do not commit anything.

## Rules the tracker follows
The tracker applies [`docs/SOP.md`](../docs/SOP.md) and [`docs/DECISIONS.md`](../docs/DECISIONS.md) section 0. If either changes, update `tracker/pipeline/build.py` (what is required) and the Definitions text in `tracker/pipeline/export.py` to match.

## Known limits
- Bookings made more than 14 days ahead are first picked up when their call date comes within 14 days. Their
  welcome call is still checked, but only against Gino's last 4 days of activity.
- "Invite accepted at" comes from the calendar response emails Close stores. If a closer's calendar doesn't send them,
  the time is unknown and the tracker says "Can't tell".
- Supabase keeps everything each run read (`call_confirm_raw_records`, as the source returned it) plus the tracker's rows and a
  copy of every tab after each run (`call_confirm_tab_snapshots`). Records pulled before Nov 13 are backfilled once from the
  saved run files.
- Show results come from #closer-eod first, then Zoom attendance. The EOD Tracker sheet, Sales Tracker and 2M tracker
  aren't checked yet.
