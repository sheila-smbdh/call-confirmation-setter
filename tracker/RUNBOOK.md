# Daily update: Call Confirmation Tracker (Gino)

Runs every day at 5:41am ET (3:41am MT), as a scheduled session, an hour before Gino's scorecard (6:41am ET) reads
what it saves. It reports on the last full day (yesterday), and also picks up anything Gino or the closers logged
overnight (late EOD posts, call outcomes, notes). Moved from 8:00pm MT on Nov 18, 2026 (Sheila). The scheduled task
keeps its name, "Gino call confirmation tracker – nightly refresh".
It refreshes the tracker: https://docs.google.com/spreadsheets/d/1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk/edit

## What this run may and may not do (Sheila's standing approval, Nov 13, 2026)

May, without asking:
- Read Close (REST API, inline `curl`, one request per command), Calendly, Slack and the tracker.
- Write to the tracker: replace the Calls, Recovery, Daily, Weekly, Definitions and Data Sources tabs (Recovery from Nov 24,
  once Sheila adds it to her standing approval; until then, skip the Recovery tab and say so in the run summary); append new rows to
  Reviews (columns A-G and L); write Management!K5 (run time) and Management!M5 (data through).
- Reviews H-J from Sheila's or Jay's decisions in #cc-gino (`slack_match.py` decides; Sheila, Nov 18: they decide
  every scorecard item in its thread and no longer edit the Reviews tab by hand). On rows whose H, I and J are all
  blank, and on rows this run filled from Slack earlier (J ends in "(Slack)") when a newer Sheila/Jay reply changes
  the decision: H = "Excused" or "Counts as a miss", I = "Approved/Decided in #cc-gino: <summary> <link>",
  J = "<name> (Slack)".
- Supabase setter-data (ref `suoblmuvrmyfmuvlhqce`), `call_confirm_` tables only: insert or update (upsert) through
  `https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/<table>`, one inline curl per file (step 12). Never delete, never
  touch any other table, never send DDL.
- Upload one staging .xlsx to Google Drive per run (title starts with `TEMP - tracker nightly`).
- Once a week, on the Tuesday-morning run (TODAY = Monday): post the weekly review reminder in #cc-gino (see step 13).
  Tuesday, not Monday (Sheila, Nov 18): Friday's scorecard posts Monday morning and its decisions come in Monday, so
  the week is only fully decided after the Tuesday-morning run.

Must not:
- Write anything to Close, Calendly or Supabase. Never delete or merge anything in Close.
- Touch Reviews column K (the Action formula), any Reviews H-J a person filled in (J not ending in "(Slack)"), or any Management
  cell other than K5 and M5 (approvals, inputs, and the formulas, including "Recovered calls that showed", which
  has added up the Daily tab since Nov 24).
- Post anything else to Slack, or message anyone.
- If a step fails, stop before swapping tabs. Leave the tracker as it was (Management!A5 will show STALE). Do not retry
  writes blindly: re-read the tracker first to see what already happened.

Follow `/root/.claude/CLAUDE.md` (Close and Supabase rules). Close calls are inline `curl` only, one per command, never
from a script. The scripts in `tracker/pipeline/` are offline: they only read and write local files.

## Commands must pass the Close guard without a prompt (this run is unattended)

The Close safety hook (`~/.claude/hooks/close-guard.py`) lets a Bash command that mentions Close run without asking
only if EVERY part of it is on its safe list. Nobody is there to approve a prompt, so one prompt stalls the whole run.
- A Bash command that calls Close may contain only: the `curl` itself, `for NAME in <plain values>; do ...; done`,
  `NAME=<plain value>`, `cd`, `ls`, `head`, `tail`, `jq`, `cat`, `wc`, `grep`, `echo`, and `python3 -c "<code>"` (no
  network or subprocess in the code). Use paths relative to the repo (`tracker/data/...`), or `cd` first.
- Everything else goes in its OWN Bash command with no Close in it: `python3 -I tracker/pipeline/<script>.py ...`,
  `rm`, `cp`, `mv`, `sha256sum`, `date`. Never chain those onto a Close `curl` with `;`, `&&` or `|`.
- No `$( )`, `$(( ))`, backticks, `eval`, `xargs`, heredocs or subshells in a Close command. Page with literal values:
  `for k in 0 100 200 300; do curl ... "&_skip=$k" -o g_call_$k.json; done`.
- Event-log paging (`_cursor`) can't be looped: send one curl per page and type the cursor value from the last page.
- If a command is ever stopped for approval anyway, don't wait: rewrite it in the allowed form and send it again.

## Fixed IDs

| What | Value |
|---|---|
| Tracker spreadsheet | `1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk` (sheet time zone: America/Los_Angeles) |
| Gino's Close user | `user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo` |
| Calendly organization | `https://api.calendly.com/organizations/a2c22cc2-7dde-4e50-bb22-4d5fc629e421` |
| Direct discovery event type | ends with `3de6762f19f4` (filtered in scope.py) |
| #call-confirmation (Zapier alerts) | `C0CF5TGANMT` |
| #closer-eod (Nero EOD posts) | `C06RE8S1L4V` |
| #cc-gino (scorecard threads, Tuesday reminder, Gino's exception requests) | `C0CG28G7TQT` |
| Supabase setter-data | ref `suoblmuvrmyfmuvlhqce`, tables `public.call_confirm_*` (`tracker/supabase/call_confirmation_schema.sql`) |
| Sheila / Jay (Slack) | `U0BM6J8KM32` / `U06Q63DTS13` |

Google Sheets edits go through Composio (`googlesheets` toolkit, account `googlesheets_gyte-urlar`); Drive uploads and
downloads through the Google Drive connector.

## Steps

Set `TODAY` = **yesterday's** date in US Eastern (YYYY-MM-DD): the last full day, the day this run reports on. The
run starts at 5:41am ET, so the real date is one day later. Every step below uses this `TODAY` (file names, `T-4`,
`Management!M5`, the run record's `today` and `data_through`), so the rows built are the same as an 8pm MT run on that
day would have built, plus whatever was logged overnight. `DIR=tracker/data/$TODAY` (gitignored; never commit it).
`P=tracker/pipeline`. Dates below: `T-4` = TODAY minus 4 days, etc.

1. **Close: users and meetings**
   - `curl -s -u "$CLOSE_API_KEY:" "https://api.close.com/api/v1/user/?_limit=200" -o $DIR/users.json`
   - `python3 -I $P/bodies.py meetings $DIR $TODAY`, then one curl per body:
     `curl -s -u "$CLOSE_API_KEY:" -X POST "https://api.close.com/api/v1/data/search/" -H "Content-Type: application/json" -d @$DIR/body_meet_created.json -o $DIR/meet_created.json`
     (same for `body_meet_starts.json` -> `meet_starts.json`).
   - After each, as a separate command: `python3 -I $P/bodies.py check RESULT`. If TRUNCATED: delete the result (`rm`,
     its own command), `bodies.py split BODY`, and
     pull both halves (`..._a.json`, `..._b.json`, saving results as `meet_starts_a.json` etc.; every result file name
     must start with `meet_`).

2. **Close: Gino's activity since T-4 (05:00 UTC)**
   - Calls: `.../activity/call/?user_id=GINO&date_created__gt=<T-4>T05:00:00&_limit=100&_skip=$k` -> `g_call_$k.json`,
     in one command: `for k in 0 100 200 300; do curl ...; done` (literal skips, never `$((...))`). Check `has_more` on
     the last page with `python3 -c`; if still true, run again with `400 500 600 700`. Empty extra pages are harmless.
   - Texts: same with `/activity/sms/` -> `g_sms_$k.json`.
   - Call Confirmation field history: `.../event/?user_id=GINO&object_type=lead&action=updated&date_updated__gte=<T-4>T05:00:00Z&_limit=50`
     -> `g_ev_<k>.json`; repeat with `&_cursor=<cursor_next>` until `cursor_next` is null (one curl per page, the
     cursor typed in literally; no `$( )`).

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

4b. **#cc-gino: decisions from Sheila or Jay (scorecard threads and exceptions)** (a subagent keeps this out of your context)
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
   - **Scorecard threads** (Sheila, Nov 18): each morning's scorecard post lists its items as numbered text
     ("3. Neal Gustafson · New booking · no-answer, missing text (...)"). Gino explains by number around noon ET;
     Sheila and Jay then decide each item in the same thread, usually by end of day. Record ONE case per item:
     `raised_ts` = `<card ts>#<item number>`, `thread_ts` = the card, `lead_names` and `call_date_mentioned` from the
     item line, `checkpoints` = the item's Reviews key suffix (New booking / Overnight -> `welcome`, Day-before ->
     `daybefore`, 5:45 cancel -> `545`, Logging -> `logging`, Follow-up -> `followup-<the card's scored day,
     YYYY-MM-DD>`, so the decision covers that one day's follow-up and not the lead's other days), `decision` "approved" for excused and "denied" for
     still a miss, `decided_by` and `decision_ts` from their reply, and a one-line `decision_summary` in their words.
     - They aim for a convention (`3, 5, 6 excused - reason`, `7 miss`), but read free text too: "should not be a
       miss", "Gino is excused", "not an error", "it's confirmed" = approved; "just missing X", "still counts",
       "should have called" = denied. A reply can cover several numbers ("3.5.6", "3, 5 and 6", "all the rest").
     - If Sheila and Jay seem to disagree, read the whole thread for the final word (a later reply that settles it,
       or one of them deferring to the other). Only if it's still not clear: "unclear", and list it in the run summary.
     - Gino's replies are context only; they never decide an item. An item nobody decided stays "no response".
     - Re-read every scorecard thread from the last 14 days each run, so a decision changed later is picked up.

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
     first read the texts between Gino and the prospect and Gino's notes on the lead (Sheila, Nov 18: he often explains
     the situation in a note): `.../activity/sms/?lead_id=<lead_id>&_limit=100` and
     `.../activity/note/?lead_id=<lead_id>&_limit=50`, one curl each. A prospect's text saying they'll attend goes in
     `text_confirms.json` (step 7b; build.py then marks the logging valid). Then read Gino's call transcript (`curl -s -u "$CLOSE_API_KEY:" ".../activity/call/<id>/?_fields=id,duration,recording_transcript"`
     for the ids in the row's `transcript_calls`: his connected calls on the lead from booking to 12 hours after he
     logged it; `phone_outcome` is true when he also logged "Confirmed not Accepted" or field 5).
     - Sheila, Nov 24: if the transcript shows the prospect **verbally confirmed** they'll be on the call (yes to the
       day and time, "I'll be there", "see you then"), it's valid, with or without a technical problem accepting:
       `{"<lead_id>": "Valid (confirmed by phone): <one-sentence reason, with the call date>"}`.
     - If the prospect confirmed and had a technical problem accepting, `"Valid (verbal + tech issue): <reason>"` as before.
     - Otherwise `{"<lead_id>": "Logging error: <one-sentence reason>"}`: no connected call, no transcript (say so, and
       name his outcome or note if he logged one, for Sheila and Jay), or the prospect didn't clearly confirm ("I'll
       check my email", "maybe", only a reschedule request).
     Re-run build.py. Don't quote transcripts at length.

7b. **Prospects who confirmed by text** (Sheila, Nov 13: a prospect's own text saying they'll be on the call counts
   as confirmed; no day-before call or 5:45 cancel is needed after it)
   - Start from the judgments already made:
     `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_raw_records?source=eq.text_confirmation&select=record_id,payload" -o $DIR/text_confirms_prev.json`
     and write them to `$DIR/text_confirms.json` as `{"<lead_id>": {"at": ..., "text": ...}}` (each payload already
     has `at` and `text`).
   - `python3 -I $P/text_confirms.py leads $DIR` -> `text_check_leads.txt`.
   - For each lead in it, one curl:
     `curl -s -u "$CLOSE_API_KEY:" "https://api.close.com/api/v1/activity/sms/?lead_id=<lead_id>&_limit=100" -o $DIR/sms_lead_<NN>.json`
   - `python3 -I $P/text_confirms.py list $DIR` prints the prospects' texts. Add to `text_confirms.json` only texts
     that clearly say they'll attend ("See you Friday!", "I'll be there", "Confirmed", "Yes, I'll be on"). Not a
     confirmation: a question, a thanks on its own, a reaction ("Liked ..."), "Done" with nothing else, a reschedule
     or cancel request. If unsure, leave it out (the item then goes to review as usual).
   - If anything was added, run `build.py` again.

7c. **Check Gino's notes before anything becomes a miss** (Sheila, Nov 18: verify his notes against Close before an
   item goes to Reviews or the scorecard)
   - List the leads with a miss in `calls_new.json` (a welcome or day-before checkpoint required and not finished, a
     daily follow-up in `fu` with `counts` "Yes" and not finished, or a 5:45 cancel required and not done);
     `python3 -c` over the file is fine.
   - For each, one curl:
     `curl -s -u "$CLOSE_API_KEY:" "https://api.close.com/api/v1/activity/note/?lead_id=<lead_id>&_limit=50&_fields=id,lead_id,date_created,user_name,note" -o $DIR/note_lead_<lead_id>.json`
     (his call notes are already in `g_call_*.json`; build.py puts them on each checkpoint as `notes`).
   - Read each miss with its notes and Gino's Close activity in that window (dial times, disposition, duration,
     voicemail, texts). If a note explains a step he couldn't do AND the activity backs it up (e.g. "straight
     disconnect, didn't ring" on a busy 0-second dial; "number disconnected" with failed dials), add to
     `$DIR/miss_overrides.json` `{"<event id>|welcome" (or "|daybefore", "|545", "|followup-<YYYY-MM-DD>"): "<what the
     note says> (<the Close evidence>)"}` and run build.py again. If the activity doesn't back the note up, it stays a miss, and reviews.py
     shows his notes on the Reviews row (column G).
   - Busy, blocked or failed 0-second dials already excuse the voicemail step automatically (Nov 18).

6b. **Close: call recovery** (Sheila, Nov 24; `tracker/pipeline/recovery.py` has the rules)
   - `python3 -I $P/bodies.py recovery $DIR $TODAY` -> `body_rec_lsc.json`, `body_rec_field.json`, `body_rec_act.json`.
     Pull each with the search curl -> `rec_lsc.json`, `rec_field.json`, `rec_act.json` (result names must start with
     `rec_`); check, split and re-pull if TRUNCATED, as in step 1.
   - `python3 -I $P/bodies.py recovery_leads $DIR $TODAY` -> `body_rec_info.json`, `body_rec_calls.json`,
     `body_rec_sms.json`, `body_rec_meet.json`, `body_rec_tasks.json`. Pull each the same way -> `rec_info.json`,
     `rec_calls.json`, `rec_sms.json`, `rec_meet.json`, `rec_tasks.json`; check, split and re-pull if TRUNCATED.
     `rec_info` is one query per lead id: if it is TRUNCATED, tell the run summary (it can't be split by date).

8. **Merge with the live tracker**
   - `mcp__Google_Drive__download_file_content` with fileId = tracker id, exportMimeType
     `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`. The file is saved by the harness; copy it to
     `$DIR/tracker_live.xlsx`.
   - `python3 -I $P/merge.py $DIR $DIR/tracker_live.xlsx` -> `calls_all.json`, `review_keys.json`, `reviews_last_row.txt`,
     `rec_prev.json` (recovery rows already on the tracker).
   - **Call recovery** (Nov 24): `python3 -I $P/recovery.py $DIR $TODAY` -> `rec_rows.json`, `rec_daily.json`,
     `rec_reviews.json`, `need_rec_cal.txt`.
     - For each line of `need_rec_cal.txt` (`<lead_id>\t<email>\t<from>`; a subagent is fine, the results are long):
       `mcp__Calendly__meetings-list_events` with the organization, `invitee_email` = the email, `min_start_time` = from.
       For every event returned that is 45 minutes long, `mcp__Calendly__meetings-list_event_invitees` with its uri, and
       append one line to `$DIR/rec_cal.jsonl`: `{"lead_id", "event_uri", "event_name", "event_type" (uri), "start"
       (start_time), "created" (created_at), "status", "scheduled_by"}`, where `scheduled_by` is the
       `invitee_scheduled_by` of the invitee with that email (null when Calendly shows none). If no event comes back,
       append `{"lead_id": ..., "event_uri": "", "event_name": "Not found in Calendly"}`. Never write to Calendly.
     - Run `recovery.py` again. `need_rec_cal.txt` should now be empty.
     - Only when a recovery day is a miss and Gino's notes on the lead explain it with Close evidence behind them (the
       same test as step 7c), add `{"<review key>": "<what the note says> (<the evidence>)"}` to `$DIR/rec_overrides.json`
       and run it again. Recovery items are coaching only; when in doubt, leave them for Sheila and Jay.
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
    one tab at a time: **Calls, Recovery, Daily, Weekly, Definitions, Data Sources** (Daily's formulas bind to the Calls
    tab that exists when Daily is copied in, and Weekly's to Daily; Daily reads Recovery through INDIRECT). The first run
    after Nov 24 has no Recovery tab to rename yet: just copy it in and rename the copy:
    1. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES`: rename the current tab to `<name> (old)`.
    2. `GOOGLESHEETS_SPREADSHEETS_SHEETS_COPY_TO`: copy the tab from the TEMP file into the tracker.
    3. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES`: rename the copy (`Copy of <name>`) to `<name>`.
    After all six: `GOOGLESHEETS_DELETE_SHEET` each `<name> (old)` tab created by THIS run (only those six; match
    by the sheet ids you renamed, never by title alone; leave every other hidden or "old ..." tab alone), then set
    indexes so the order is Management (0), Reviews (1), Call Confirmation>> (2), Calls (3), Daily (4), Weekly (5),
    Call Recovery>> (6), Recovery (7), Definitions (8), Data Sources (9). "Call Confirmation>>" and "Call Recovery>>"
    (renamed by Sheila Nov 24) are Sheila's divider tabs:
    never edit, rename or delete them. Management uses INDIRECT for Calls and Daily, so it keeps working through the
    swap.
    Google Sheets allows about 60 reads per minute. If a call returns 429 (quota), wait 60 seconds and retry that
    one call; it did not go through.

11. **Append Reviews and stamp the time**
    - If `reviews_append.json` is non-empty: `GOOGLESHEETS_UPDATE_VALUES_BATCH` with `valueInputOption`
      `USER_ENTERED` and `data` = that file's list. (A-G and L; H-J only for rows already decided in Slack.)
    - If `reviews_fill.json` is non-empty: same call with that list (fills H-J from Sheila's and Jay's #cc-gino
      decisions: "Excused" or "Counts as a miss"). Re-check first with `GOOGLESHEETS_BATCH_GET` that each of those
      H:J ranges is still blank, or still holds what this run wrote from Slack earlier (J ends in "(Slack)"); drop
      any a person has filled in since.
    - List in the run summary every Reviews row still undecided and why (no reply yet, "unclear", or no item matched).
    - `GOOGLESHEETS_UPDATE_VALUES_BATCH`: `Management!K5` = now in Pacific time as `YYYY-MM-DD HH:MM` (the real
      time, i.e. the morning after TODAY), and `Management!M5` = TODAY (the data-through day).
    - Verify with `GOOGLESHEETS_BATCH_GET` of `Management!A1:A5`, `Management!A15:O16` and the last two rows of
      `Daily`: no `#REF!`, `#N/A`, `#ERROR!` or `#VALUE!`; A5 starts with "Up to date". If not, report it (step 14).

12. **Save everything to Supabase** (setter-data, `call_confirm_` tables). `RUN_ID` = the run's real start time, e.g.
    `2026-11-19T05:41-05:00`. In the run record, `today` and `data_through` are both TODAY (yesterday's date).
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

13. **Weekly reminder in #cc-gino** (`C0CG28G7TQT`), only on the run where TODAY is a Monday (it runs Tuesday
    morning, once Friday's scorecard decisions from Monday are in), after step 12: read `Management!A1:A4` and the row
    for the week that ended the day before TODAY (Monday to Sunday), then post one message:
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
Daily follow-up calls (Sheila, Nov 19; scored from Nov 19, count toward KPI 1): bookings made 2+ days out whose invite
isn't accepted need a call each weekday between the welcome call and the day before (double dial + voicemail, no
text). They're stored per call in `fu`, shown in the Calls tab's last columns and the Daily tab's "Daily follow-up
calls" block (both added at the end so the Management tab's fixed column references don't move), and each missed day
is its own Reviews item (`<event>|followup-<date>`).

The tracker applies [`docs/SOP.md`](../docs/SOP.md) and [`docs/DECISIONS.md`](../docs/DECISIONS.md) (sections 00000 to 0, newest first). If either changes, update `tracker/pipeline/build.py` (what is required) and the Definitions text in `tracker/pipeline/export.py` to match.

## Known limits
- Every run rebuilds calls from 3 days ago to 14 days ahead (Nov 19, for the daily follow-up calls), so step 5 looks up
  more Calendly invitees than before. A welcome call or follow-up day older than the 4 days of Gino's activity a run
  pulls keeps the result an earlier run gave it (`merge.py`).
- Bookings made more than 14 days ahead are first picked up when their call date comes within 14 days. Their
  welcome call is still checked, but only against Gino's last 4 days of activity.
- "Invite accepted at" comes from the calendar response emails Close stores. If a closer's calendar doesn't send them,
  the time is unknown and the tracker says "Can't tell".
- Supabase keeps everything each run read (`call_confirm_raw_records`, as the source returned it) plus the tracker's rows and a
  copy of every tab after each run (`call_confirm_tab_snapshots`). Records pulled before Nov 13 are backfilled once from the
  saved run files.
- Show results come from #closer-eod first, then Zoom attendance. The EOD Tracker sheet, Sales Tracker and 2M tracker
  aren't checked yet.
