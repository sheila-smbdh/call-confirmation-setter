# Handoff: pre-call confirmation analysis (Nov 4, 2026)

Start here in a new session. This brief holds everything learned so far about how closers and setters confirm calls before they happen, what it does to show rate, the proposal Sheila is taking to leadership, and how to pull more data.

Read `docs/DECISIONS.md` too. It defines the Call Confirmation Specialist role.

## The goal

Sheila wants a pre-call confirmation workflow for **setter-set calls**, backed by data. The October sample is small, so the next step is to **pull more data** (earlier months) and re-run the analysis.

Scope, as Sheila corrected it:
- The **Call Confirmation Specialist** handles confirmation for **direct-to-closer** calls only.
- **Setter-set** calls are on the **setter and closer**. The specialist does not touch them.

## Where we left off

Sheila is sending this proposal to leadership. It covers setter-set calls only.

1. **Setter, day before:** a reminder that says the closer has prepared, asks the lead to join on a laptop, and prompts them to accept the calendar invite.
2. **Setter, morning of the call:** a warm handoff with the Zoom link.
3. **Closer, about 1 hour before:** one line only.

How it gets measured:
- Save all three as Close SMS templates, so adoption shows up via `template_id`.
- Run it for 4 weeks.
- Compare the setter-set show rate against October's **66%**.

Sheila's draft templates, with suggested edits:
- **Setter day before:**
  > "Hey [First Name]! Just a reminder about your call tomorrow with [Closer Name] at [Time]. He's already reviewed your application and my notes, and has a presentation ready for you. Please hop on from your laptop so you can see everything he's sharing. And if you haven't yet, make sure you accept the calendar invite, since our system may automatically cancel the call if it's not accepted. Let me know if you can't find it, and I'll resend it to your email."
  - Add a reply prompt: "Still good for [Time] [TZ]?"
  - Add the time zone.
  - Use the closer's name instead of "He's".
  - Check the auto-cancel claim is true; if not, soften it.
  - Shorten the last line.
- **Setter day of:**
  > "Hey [First Name]! Excited to hear how your call with [Closer Name] goes today at [Time]. Let me know if I can help with anything!"
  - Add the Zoom link.
  - Send it 2 to 3 hours before the call.
- **Closer day of (proposed):** "Hey [Name], [Closer] here. Looking forward to talking at [Time]!"
  - Send it a few hours after the setter's morning text.

The full leadership message draft is in the report's comment thread. The report is published privately at https://claude.ai/artifact/WSFZVSxhYic1cKJ2JSfMgH, and a copy is at `analysis/precall-confirmation/report.html`.

## Findings (Oct 3 to Nov 2, 2026; 45-minute closer calls)

### Closer confirmation habits

| Closer | Calls | Day before (closer's own) | Day of (closer's own) | Pattern |
|---|---|---|---|---|
| Adam L | 59 | 11% | **86%** | Saved SMS template every morning, about 2 hours before the call |
| Nick | 79 | 14% | 5% | Writes a day-before text, but **33 of 34 were unsent drafts** in Close |
| Solomon | 79 | 9% | 14% | Only for at-risk calls (invite unaccepted or "maybe") |
| Tyler | 59 | 28% | 25% | Sometimes |
| Julien | 12 | 33% | 25% | Sometimes (small sample) |
| Oliver | 30 | 9% | 33% | Sometimes, on the day |
| Kevin, Harry, Daniel, Jay Z, Omar, Owen, VeJohn | 47–116 each | 4–10% | 8–20% | Rarely |

- Nobody confirms by phone. Harry made a handful of calls.
- Day-before contact is almost entirely the automated "NEW Pre-Call Workflow" email sequence, which reaches 33–73% of calls.
- These rates are a ceiling, because they include replies to leads who texted first.

### Confirmation vs show rate across closers

Show rates here are from the tracker for October.
- **Day-of confirmation:** rank correlation 0.65 with show rate (p ≈ 0.02); straight-line correlation 0.42 (p ≈ 0.15).
- **Day-before confirmation:** no meaningful link.
- Closers who confirm at least a quarter of calls on the day showed **74%**; everyone else showed **65%**.
- On direct calls only, the rank correlation drops to 0.49.
- Call by call, direct calls with a day-of touch showed 64%, against 70% without one. That comparison is biased: day-of texts often go to leads who already look shaky.
- Direct calls with a day-before touch showed 73% (24/33), against 64%.

### Setter-set vs direct

| | Setter-set | Direct |
|---|---|---|
| Calls | 197 (23%) | 678 (77%) |
| Show rate (EOD Tracker) | 66% (95/145) | 68% (302/442) |
| Any day-of touch (setter or closer) | 40% | 22% |

Setter-set calls by who touched the lead, day before or day of (145 with a show result):

| Who touched | Show rate |
|---|---|
| No one | 64% (45/70) |
| Closer only | 60% (15/25) |
| Setter only | 69% (27/39) |
| Both | 73% (8/11) |
| Setter texted on the day | 74% (25/34) |
| Closer texted on the day, setter didn't | 57% (12/21) |
| Any day-before touch (booked 2+ days ahead) | 61%, same as without |

- Of the three workflows Sheila asked about, "setter does both days" happened only 3 times and "closer does both days plus setter day-of" never happened. Neither can be evaluated without more data.
- Setters who send closer-call reminders: **Jordan K, Jose and Bali**.
- Quinn and Yobani's reminders were for their own 15-minute intro calls.
- **Dave and Gabriel had no October activity in Close.** Dave's Close user ID is unconfirmed; ask Sheila.

## Method and definitions

- **Calls:** 45-minute meetings (`duration` 2700) on active closers' calendars.
  - One per lead and start time; only calls that have already happened.
  - Closer roster comes from the tracker's `/api/read/roster`.
  - "Jay Z" is assumed to be Jordan Zadrozny (`jordan@`).
- **Counted touches:** outbound SMS with status `sent` or `delivered`, outbound calls, and non-sequence emails.
  - Each must be sent after the booking and before the call.
  - Times are converted to ET; "day of" and "day before" are ET calendar days.
- **Excluded touches:**
  - Anything within 1 hour of booking.
  - Booking welcome texts (regex in `analyze.py`).
  - Texts whose wording repeats on more than 25 leads and doesn't mention the call (bulk blasts).
  - Drafts and failed sends.
  - Anything in the last 10 minutes before the call.
  - Automated sequence emails (counted separately).
- **Day-before denominator:** only calls booked 2+ days ahead.
- **Setter-set:** within the 21 days before booking (up to 2 hours after it), a setter did one of these on the lead:
  - held a meeting with them,
  - logged a call with the outcome "Conversation: set to closer" (`outcome_034XYnwGD1sz2iKRzZAeuk`),
  - had a call of 2+ minutes with them.
  
  Everything else is direct.
- **Setters:**

  | Setter | Close user ID |
  |---|---|
  | Bali | `user_c0wPSKtEPsqkIh08OnjiGaj6XHeFBjGSp2jyVxAggDl` |
  | Jose | `user_msFtSHmZcoRAYvHX8aGrnygBzOy4u1GnLrRSFfIdcgk` |
  | Jordan K | `user_3IrYZLUcCBZrg2mb49wCybrxGBFTCxa5eqTHhE1ApuC` |
  | Yobani | `user_TH3XzqxRNb7WhZ5taaJ9v3df27VAaU6KvCnFlCUbq9v` |
  | Quinn | `user_fXLAvRIRIJxMAgcaYa2hH14SuwQphwF5aC9vtvouHob` |
  | Dave | `user_xKqE1WtzdG6eCYm7ZtgPqsTjl2mjAXw0bvaifoVQPtc` (unconfirmed) |
  | Gabriel | `user_rtKYgVTxSrwnTd5wJJA5Y6jr4gteTRTV1BloPCzuWXQ` |
- **Per-call show result:** the EOD Tracker sheet (`11PnemLh8wDT-baqbYBcW3cw0zv4vl82J7NumHTh7dCc`, Sheet1).
  - Columns A to F, plus X to AA: `showed_leads`, `no_showed_leads`, `cancelled_leads`, `rescheduled_leads`.
  - Matched on closer, ET date and lead ID.
  - Showed counts as a show. No-showed and cancelled count as no-shows.
  - Only 587 of 875 calls had an EOD entry.

## How to pull the data (gotchas)

- **Close safety rules (user CLAUDE.md):** read-only; inline `curl` only; one request per command; no scripts that call Close.
  - Reads need no approval.
  - Any write to Close needs Sheila's explicit approval.
  - Never delete anything in Close.
- **Endpoint:** use the search API, `POST https://api.close.com/api/v1/data/search/`, with `_limit: 200`.
  - Object types: `activity.meeting`, `activity.sms`, `activity.call`, `activity.email`.
  - Example query shape for meetings:
    ```json
    {"query":{"type":"and","queries":[
      {"type":"object_type","object_type":"activity.meeting"},
      {"type":"field_condition","field":{"type":"regular_field","object_type":"activity.meeting","field_name":"starts_at"},
       "condition":{"type":"moment_range","on_or_after":{"type":"fixed_utc","value":"2026-10-03T04:00:00Z"},"before":{"type":"fixed_utc","value":"2026-11-03T05:00:00Z"}}},
      {"type":"field_condition","field":{"type":"regular_field","object_type":"activity.meeting","field_name":"duration"},"condition":{"type":"number_range","gte":2700,"lte":2700}},
      {"type":"field_condition","field":{"type":"regular_field","object_type":"activity.meeting","field_name":"user_id"},"condition":{"type":"reference","reference_type":"user_or_group","object_ids":["user_..."]}}]},
     "_fields":{"activity.meeting":["id","lead_id","user_id","starts_at","status","title","date_created","attendees","outcome_id"]},"_limit":200}
    ```
  - Direction filters use a `term` condition on `direction`.
- **Search cursors expire within seconds.** Don't page with them. When a response returns 200 rows with a cursor, split the date window in half and re-query each half. Some reps need windows of an hour or less on blast days.
- **Direction values:** SMS and calls use `"outbound"`. Emails use **`"outgoing"`**; `"outbound"` returns nothing.
- **SMS status:** filter to `sent` or `delivered`. Drafts exist, as Nick's day-before texts show.
- **Volume:** busy reps send 1,000 to 3,700 outbound texts a month. Parallel subagents, one per group of reps, worked well; each saves raw JSON to a scratch folder.
- **EOD Tracker:**
  - The Drive connector only returns the whole 3.5 MB file.
  - Composio's `GOOGLESHEETS_BATCH_GET` in the remote workbench can read just the needed ranges.
  - Composio's download URL is blocked by this environment's network. Print a compact extract (ET date, closer, last 10 characters of each lead ID by outcome) and save it locally.
- **Tracker API:** `/api/read/closers?month=YYYY-MM` gives per-closer `values.show_pct`, `sched` and `live`.

## Code in this repo

`analysis/precall-confirmation/`:

| File | What it does |
|---|---|
| `analyze.py` | Per-closer confirmation rates and message samples. Reads `close/raw/{closer}_{type}_*.json` next to the script. |
| `split.py` | Setter-set vs direct split, per-call show rates, and touch patterns. Also reads `close/setter/*.json` and `eod/eod_oct.txt`. Writes `split_rows.json`. |
| `report.html` | Copy of the published report. |

- Both scripts are offline. They make no network calls; run them with `python3 -I`.
- Raw data is **not** committed because it contains lead PII. `.gitignore` excludes those folders.
- To re-run, pull the data again into those folders using the recipe above.

## Next steps

1. **Grow the sample.** Pull August and September 2026, and earlier if the EOD Tracker covers it, for closer meetings, closer and setter SMS/calls/emails, setter meetings, and EOD outcomes. Then re-run `split.py`. The goal is to evaluate:
   - setter-only touches,
   - setter plus closer on the day,
   - day-before touches.
2. **Use a better outcome than texts.** Meeting `attendees[].status` (`yes`/`noreply`) shows whether the lead accepted the invite. The decisions doc defines **confirmed = invite accepted**. Test whether acceptance predicts showing, and whether setter day-before texts raise acceptance.
3. **Separate proactive from reactive touches.** Proactive texts are sent before the lead wrote. Reactive ones are replies.
4. Confirm Dave's Close user and whether Gabriel is still setting.
5. Once the new workflow runs, track template adoption via `template_id` against show rate, and compare it to the October baseline.

## Permission prompts (not set up yet)

**The fastest fix is mode, not settings.** Picking **Auto** from the mode dropdown next to the prompt box, where the organization allows it, runs most commands without asking.

**For a permanent fix, Sheila adds the allowlist herself.** Claude isn't allowed to change permission settings. The proposed allowlist pre-approves **read-only** commands only:
- Close GET calls and search calls written in the exact CLAUDE.md `curl` form
- Tracker reads
- Running the offline analysis scripts

It also denies anything that would change data in Close. Writes to Close would still prompt, and CLAUDE.md still requires Sheila's approval for them.

Save it as `.claude/settings.json` in this repository and commit it:

```json
{
  "permissions": {
    "allow": [
      "Bash(curl -s -u \"$CLOSE_API_KEY:\" \"https://api.close.com/api/v1/*)",
      "Bash(curl -s -u \"$CLOSE_API_KEY:\" -X POST \"https://api.close.com/api/v1/data/search/\" *)",
      "Bash(curl -s -H \"Authorization: Bearer $TRACKER_READ_TOKEN\" \"https://smbdh-2m-tracker.vercel.app/api/read*)",
      "Bash(python3 -I analysis/precall-confirmation/*)"
    ],
    "deny": [
      "Bash(curl * -X PUT*)",
      "Bash(curl * -X PATCH*)",
      "Bash(curl * --request *)",
      "Bash(curl -s -u \"$CLOSE_API_KEY:\" \"https://api.close.com/api/v1/* -X *)",
      "Bash(curl -s -u \"$CLOSE_API_KEY:\" \"https://api.close.com/api/v1/* -d *)",
      "Bash(curl -s -u \"$CLOSE_API_KEY:\" \"https://api.close.com/api/v1/* --data*)"
    ]
  }
}
```

Your existing Close safety hook already blocks any deletion, so there is no separate deny rule for it here.
