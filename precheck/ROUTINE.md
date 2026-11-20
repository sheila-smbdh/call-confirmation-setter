# Afternoon pre-check: what would be a miss on Gino's next scorecard

Runs Monday to Friday at **4:37pm MT (6:37pm ET)** as a scheduled session, and posts by **5:30pm MT (7:30pm ET)**, 30
minutes before Gino's shift ends (6pm MT / 8pm ET, `docs/SOP.md`). It checks today's work the same way the morning
tracker run will, and posts one message in #cc-gino tagging Gino with every item that would show as a miss on the next
scorecard, plus the 5:45 cancels coming up, so he can fix them before he logs off (Sheila, Nov 20).

- Monday to Thursday: covers today, for tomorrow's scorecard. Friday: covers Friday, for Monday's scorecard.
- Saturday and Sunday: nothing is sent.
- It is a heads-up only. It writes nothing to the tracker or Supabase; the morning run (`tracker/RUNBOOK.md`) still
  decides what goes to Reviews and the scorecard.

## What this run may and may not do

May, without asking (once Sheila adds this run to her standing approvals):
- Read Close (REST API, inline `curl`), Calendly, Slack (#call-confirmation) and Supabase setter-data `call_confirm_*`
  tables (GET only).
- Post **one** message per day to #cc-gino (`C0CG28G7TQT`): the contents of `$DIR/message.txt`.
- If a step fails or the post would land after 6pm MT: one Slack DM to Sheila (`U0BM6J8KM32`) saying what went wrong.

Must not:
- Write to Close, Calendly, Supabase, the tracker sheet, Drive or anything else.
- Post anything else to Slack, reply in threads, or message anyone else.
- Commit anything. The working files contain lead names: keep them in `precheck/data/` (gitignored).

Follow `/root/.claude/CLAUDE.md`. Close and Supabase calls are inline `curl` only, one request per command, in the form
`tracker/RUNBOOK.md` describes under "Commands must pass the Close guard" (no `$( )`, no scripts around a Close call).

## Time budget

The post must be in Slack by 5:30pm MT. The steps below are ordered so the slow, slow-changing reads (Calendly) come
first and Gino's own activity is pulled last, as close to the post as possible. If it is already 5:30pm MT when you
reach step 6, skip anything optional and post. If it would be after 6pm MT, don't post: DM Sheila instead (step 8).

## Steps

`TODAY` = **today's** date in US Eastern (YYYY-MM-DD) (not yesterday, unlike the morning run). If it is a Saturday or
Sunday, stop. `DIR=precheck/data/$TODAY`, `P=tracker/pipeline`. `T-4` = TODAY minus 4 days, etc.
`mkdir -p $DIR` (its own command).

1. **Start from this morning's run** (Supabase reads, one curl each):
   - `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_runs?select=run_id,today,status&order=run_id.desc&limit=1" -o $DIR/run_prev.json`
     Call its `run_id` RUN. If its `status` isn't `ok`, or its `today` isn't the day before TODAY (the morning run
     runs every day, weekends included), the morning run didn't finish: skip the two `last_run_id` reads below and fetch every invitee
     in step 3.
   - Calendly invitees it already looked up: `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_raw_records?source=eq.calendly_invitee&last_run_id=eq.<RUN>&select=payload&limit=5000" -o $DIR/prev_invitees.json`
   - #call-confirmation alerts it already read: same with `source=eq.slack_call_confirmation` -> `$DIR/prev_alerts.json`
   - Its judgments, any run (each is per lead): same without the `last_run_id` filter, for `source=eq.judgment_override`
     -> `$DIR/prev_overrides.json`, `source=eq.lead_fix` -> `$DIR/prev_lead_fix.json`, `source=eq.text_confirmation`
     -> `$DIR/prev_text.json` (select `record_id,payload`).
   - Reviews keys already on the tracker: `curl -s "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/call_confirm_reviews?select=review_key&limit=5000" -o $DIR/review_keys_prev.json`
   - Turn them into the pipeline's files (its own command): `python3 -I precheck/seed.py $DIR`. It writes
     `cal_invitees.jsonl`, `slack_alerts.jsonl`, `overrides.json`, `lead_fix.json`, `text_confirms.json` and an empty
     `eod_recent.json` (show results don't matter here).

2. **Calendly events**, exactly as runbook step 3 (T-3 to T+14) (a subagent pages them in order into
   `$DIR/cal_events.jsonl` with `calx.py`).

3. **Close users and meetings, scope, invitees**
   - Runbook step 1 (users, `bodies.py meetings $DIR $TODAY`, the two meeting searches, `bodies.py check`, split if
     TRUNCATED).
   - `python3 -I $P/scope.py $DIR $TODAY`. For each URI left in `need_invitees.txt` (normally only bookings made since
     this morning), `mcp__Calendly__meetings-list_event_invitees` and append to `$DIR/cal_invitees.jsonl` as runbook
     step 5 describes.

4. **#call-confirmation alerts since this morning's run**: read `C0CF5TGANMT` from 5:00am ET today to now and append
   new alerts (a `ts` not already in the file) to `$DIR/slack_alerts.jsonl` in runbook step 4's format. (If the morning
   run didn't finish, read from T-4 00:00 ET instead.)

5. **Close: status history and calendar responses**: runbook step 6 (`bodies.py leads`, `lsc_1.json`, `acc_1.json`).
   The status-history search is usually TRUNCATED (30 days of changes): split and re-pull until every part is OK
   (Nov 20 test: five splits, all `lsc_*` files).

6. **Close: Gino's activity, pulled last**: runbook step 2 (calls, texts, Call Confirmation field history since T-4
   05:00 UTC). Then build in preview mode:
   `python3 -I $P/build.py $DIR $TODAY preview`
   Skip runbook steps 7, 7b and 7c (transcripts, new prospect texts, notes): the morning run does those before anything
   becomes a miss, and the post tells Gino to leave a note where one explains a step.

7. **Write and post**
   - `python3 -I precheck/preview.py $DIR $TODAY` -> `$DIR/message.txt`; it prints `OK {...}` with the counts.
   - Read the message once. Check that the items make sense against `calls_new.json` (no item for a call that was
     cancelled, no item dated another day except logging errors).
   - Read the last few messages in `C0CG28G7TQT` (`slack_read_channel`). If today's pre-check is already there, stop,
     so nothing posts twice.
   - If it is before 6pm MT: `slack_send_message` to `C0CG28G7TQT` with the exact text of `message.txt` (it tags Gino
     as `<@U0CFPJZQHGQ>`). Post it even when nothing is open (it then says so).

8. **If anything fails** before the post, or it is already 6pm MT: post nothing to #cc-gino. DM Sheila one line: "Gino's
   pre-check wasn't sent: <which step and why>." If the post call fails partway, read the channel before retrying.

9. **Finish** with one line: what was posted (items to fix, cancels coming up, the activity time it used) or why
   nothing was, and how long the run took (so the 4:37pm MT start can be moved if it runs close to 5:30).
