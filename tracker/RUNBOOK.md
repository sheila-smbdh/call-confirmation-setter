# Nightly update: Call Confirmation Tracker (Gino)

Runs every day at 8:00pm Mountain (two hours after Gino's 6pm MT shift ends), as a scheduled session.
It refreshes the tracker: https://docs.google.com/spreadsheets/d/1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk/edit

## What this run may and may not do (Sheila's standing approval, Nov 13, 2026)

May, without asking:
- Read Close (REST API, inline `curl`, one request per command), Calendly, Slack and the tracker.
- Write to the tracker: replace the Calls, Daily, Weekly, Definitions and Data Sources tabs; append new rows to
  Reviews (columns A-G and L only); write Management!K5 (run time) and Management!M5 (data through).
- Upload one staging .xlsx to Google Drive per run (title starts with `TEMP - tracker nightly`).
- On Sundays only: post the weekly review reminder in #cc-gino (see step 12).

Must not:
- Write anything to Close, Calendly or Supabase. Never delete or merge anything in Close.
- Touch Reviews columns H-K (Sheila's and Jay's decisions, and the Action formula) or any Management cell other
  than K5 and M5 (approvals, recovered calls, inputs).
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
| #cc-gino (Sunday reminder) | `C0CG28G7TQT` |
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
   - `python3 -I $P/reviews.py $DIR` -> `reviews_append.json`.

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
    After all five: `GOOGLESHEETS_DELETE_SHEET` each `(old)` tab, then set indexes so the order is Management (0),
    Reviews (1), Calls (2), Daily (3), Weekly (4), Definitions (5), Data Sources (6). Management uses INDIRECT for
    Calls and Daily, so it keeps working through the swap.

11. **Append Reviews and stamp the time**
    - If `reviews_append.json` is non-empty: `GOOGLESHEETS_UPDATE_VALUES_BATCH` with `valueInputOption`
      `USER_ENTERED` and `data` = that file's list. (It writes A-G and L only; H-K stay for Sheila and Jay.)
    - `GOOGLESHEETS_UPDATE_VALUES_BATCH`: `Management!K5` = now in Pacific time as `YYYY-MM-DD HH:MM`, and
      `Management!M5` = TODAY.
    - Verify with `GOOGLESHEETS_BATCH_GET` of `Management!A1:A5`, `Management!A15:O16` and the last two rows of
      `Daily`: no `#REF!`, `#N/A`, `#ERROR!` or `#VALUE!`; A5 starts with "Up to date". If not, report it (step 13).

12. **Sundays only (TODAY is a Sunday in ET): weekly reminder in #cc-gino** (`C0CG28G7TQT`), after step 11:
    read `Management!A1:A4` and the row for the week that ends today, then post one message:
    ```
    <@U0BM6J8KM32> <@U06Q63DTS13> Weekly call confirmation review, week of <Mon date>–<Sun date>.
    • Compliant: <Yes/No/WAITING> (KPI 1 confirmation <x%> · KPI 2 speed to lead <y%> · KPI 3 logging <met/not met>)
    • Reviews to decide: <n> (Reviews tab, rows <list>)  — or "none"
    • Please each approve the week on the Management tab (cells D<row> and E<row>) once reviews are decided.
    Tracker: https://docs.google.com/spreadsheets/d/1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk/edit
    ```
    Use the numbers exactly as the tracker shows them. No other Slack posts.

13. **Finish**: print a short run summary (rows rebuilt, new Reviews rows, any warnings). Leave the TEMP file in Drive
    (Sheila deletes it; nothing in Drive is deleted by this run). Do not commit anything.

## Known limits
- Bookings made more than 14 days ahead are first picked up when their call date comes within 14 days. Their
  welcome call is still checked, but only against Gino's last 4 days of activity.
- "Invite accepted at" comes from the calendar response emails Close stores. If a closer's calendar doesn't send them,
  the time is unknown and the tracker says "Can't tell".
- Show results come from #closer-eod first, then Zoom attendance. The EOD Tracker sheet, Sales Tracker and 2M tracker
  aren't checked yet.
