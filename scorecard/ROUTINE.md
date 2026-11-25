# Morning scorecard: Gino's daily card in #cc-gino

Runs Monday to Friday at 6:41am ET as a scheduled session. It reads what this morning's tracker run (5:41am ET) saved in Supabase,
draws one PNG and posts it to #cc-gino (`C0CG28G7TQT`), tagging Gino. He replies in the post's thread with why for each
numbered item, so Sheila and Jay have his side before they decide the Reviews tab.

- Tuesday to Friday: the card covers the day before.
- Monday: the card covers Friday, plus one "Weekend (not scored)" line for Saturday and Sunday.
- Saturday and Sunday: nothing is sent.

## What this run may and may not do (Sheila's standing approval, Nov 13, 2026)

May, without asking:
- Read Supabase setter-data `call_confirm_*` tables through `https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1/...`
  (GET only, inline curl).
- Post one message per run to #cc-gino (`C0CG28G7TQT`): the scorecard PNG with the comment in `message.txt`.
- If the data is stale or a step fails: one Slack DM to Sheila (`U0BM6J8KM32`) saying what went wrong.

Must not:
- Write to Supabase, Close, Calendly, the tracker sheet or anything else.
- Post anything else to Slack, reply in threads, or message anyone else.
- Commit anything. The working files contain lead names: keep them in `scorecard/data/` (gitignored).

Follow `/root/.claude/CLAUDE.md`. Supabase calls are inline curl only, never from a script.

## Steps

`TODAY` = today's date in US Eastern (YYYY-MM-DD). `DIR=scorecard/data/$TODAY`.

1. **Plan**: `python3 -I scorecard/plan.py $TODAY $DIR`.
   - If it prints `SKIP`, stop. Post nothing.
   - Otherwise it prints six lines, `<file> <url>`. For each, run `curl -s "<url>" -o $DIR/<file>`, copying the URL
     exactly (one request per command; Sheila's Supabase rule). The last two (`rec_days.json`, `rec_weeks.json`) are call recovery, from Nov 24. Each file must be a JSON list; if one holds an
     error object instead, treat it as a failed step (step 5).
2. **Build**: `python3 -I scorecard/build_card.py $DIR`.
   - `OK ...`: carry on.
   - `STALE ...`: this morning's tracker run didn't finish (or is still running). Post nothing to #cc-gino. DM Sheila one line:
     "Gino's scorecard wasn't sent: <the STALE line>. Check this morning's tracker run." Then stop.
3. **Render**: `node scorecard/render.js $DIR` -> `$DIR/scorecard.png`. Look at it once: the date in the title is the
   scored day, seven tiles in the Call confirmation row (Follow-ups was added Nov 19), a Call recovery row of four + three tiles
   (Nov 24; on Mondays also the "Last week's call recovery" box), and the number of items in "Reply with why" matches the
   `to_explain` count from step 2 (recovery items come last and say "Recovery").
4. **Post** (once only). First read the last few messages in `C0CG28G7TQT` (`slack_read_channel`); if a scorecard
   for this day is already there, stop, so nothing posts twice.
   - `slack_get_file_upload_url` with filename `gino-scorecard-<day>.png`, `content_length` = the file's size in
     bytes (`stat -c %s $DIR/scorecard.png`), alt text "Gino's call confirmation scorecard for <day>".
   - `URL='<the exact upload URL>' && curl -sS -X POST "$URL" -H "Content-Type: image/png" --data-binary @$DIR/scorecard.png`
   - `slack_complete_file_upload` with `channel_id` `C0CG28G7TQT` and `initial_comment` = the exact contents of
     `$DIR/message.txt` (it tags Gino as `<@U0CFPJZQHGQ>`).
5. **If anything fails** before the post: post nothing to #cc-gino, DM Sheila one line saying which step failed and
   why. If the upload fails partway, read the channel before retrying.
6. **Finish** with one line: what was posted (day, targets hit, items to explain) or why nothing was.

## How decisions get back to the tracker

The comment (`message.txt`) lists the numbered items as text under the image. Gino explains by number around noon
ET; Sheila and Jay decide each item in the same thread ("3, 5 excused - reason" / "7 miss", or free text). The next
morning's tracker run reads the thread and fills the Reviews tab (H-J) for them, so they only open the tracker for
the weekly approval on Tuesdays (Sheila, Nov 18).

## How the card is counted

See the docstring at the top of `scorecard/build_card.py`. In short, a miss is an open row on the tracker's Reviews
tab for that day, so the card and the tracker always agree. Rows Sheila or Jay already marked Excused (for example,
approved in #cc-gino) leave the card. Call recovery (Nov 24) comes from the recovery_day records the morning run saves
in Supabase (`tracker/pipeline/recovery.py`): it's information only, never part of the "X of 7 hit" pill or the bonus.
