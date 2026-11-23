# Proposal: call recovery on Gino's scorecard and tracker

Status: **draft for Sheila's review.** Nothing here is built or live. It sits on a branch until Sheila approves it. When she does, the build updates `docs/DECISIONS.md`, the pipeline, the scorecard and the runbook.

Based on the Call Confirmation Quick Guide (Jay, Nov 3, as Sheila pasted it on Nov 23) and the decisions log (rev 8). The Close data is as of Nov 23.

Mockups (sample data, made-up names):
- `mockup/scorecard.png`: the daily card with the recovery row filled in.
- `mockup/tracker-recovery.png`: the new Recovery tab, the new Daily and Weekly columns, and the changes to the Management tab.

---

## What I found first

1. **Gino has logged no recoveries yet.** There are 4 "Call Confirmation Specialist" activities in Close, all logged by Jay on Nov 3–9, before Gino started. So far no one has measured recovery, and the bonus is still typed in by hand.
2. **There's enough volume to measure.** Since Nov 10, closers moved 70 opportunities to *No Show/Cancel* and 38 to *Reschedule Request* in the Sales pipeline. That's roughly 50 a week. Some are closers' follow-up calls, so they're out of scope.
3. **The pasted SOP and the repo's SOP disagree on where recoveries book.**
   - Pasted (Nov 3 text): every recovery goes to the closers' round robin, `sdrb_c2_startnow`.
   - Repo `docs/SOP.md` and decisions log rev 7 (Nov 19): reschedule requests go to the closers, and no-shows and cancels go to the setter calendar, `emorg_intro`.
   - This matters for the bonus: we need to know which booked call has to "show". See decision 3.
4. **The SOP says when he recovers, but not what one touch is.**
   - Confirmation spells out each touch: double dial, then voicemail, then text where it applies.
   - Recovery has a No-show text and a Cancel text, but no rule for when they're sent. See decision 2.
5. **Two open items in the decisions log are now answered by the SOP:**
   - Cancel cadence: same day, then once a day.
   - Window: 5 business days, for no-shows, cancels and reschedule requests alike.
6. **The recovery smart views aren't visible through the API.** "Newest - No Shows", "Newest - Cancels", "Newest - Reschedule Requests" and "Backlog" don't appear in the smart view list. They're probably private to Gino. The tracker will find recovery cases from the pipeline stages and Calendly instead, the same way confirmation uses Slack alerts first.

---

## The core idea: one "case" per lost call

Confirmation is checked call by call, at checkpoints. Recovery works differently. A case:
- opens when a call is lost;
- stays open up to 5 business days;
- ends when the lead is rebooked, the window runs out, or the lead says no;
- pays only later, if the new call shows.

So the tracker gets **one row per lost call (a "case")** with a day-by-day touch grid. The scorecard reads its daily numbers from those rows.

**A case opens when (proposed):**

| Type | Found by | First touch due | Then |
|---|---|---|---|
| Reschedule request | Opportunity moved to *Reschedule Request* (Sales pipeline) | Within 15 min if it comes in during his shift; first 30 min of his next shift if it comes in overnight (like speed to lead) | Once a day |
| No-show | Opportunity moved to *No Show/Cancel* after the call time, or a same-day cancel (show-rate rule, decisions log section 8) | Next business day | Once a day |
| Cancel | Calendly cancel, or *No Show/Cancel* before the call day | Same day (next shift if it comes in after his shift) | Once a day |

**A case ends when:**
- he rebooks the lead;
- 5 business days pass;
- the lead says "not interested" or "already bought";
- the closer already spoke with the lead (the closer handles it);
- he set a callback task, which moves the next touch due to the task's date;
- the lead has already been rebooked twice (the max-2 rule).

Only in-scope calls count: discovery calls booked directly with an Enrollment Advisor, the same scope as confirmation. Calls lost before the start date (the backlog) are never scored for touches. If one of them rebooks and shows, it still earns the $50 (decisions log section 7).

**Credit and bonus:** these follow the existing rules.
- He gets credit if he logged any contact in Close after the lost call and before the rebook, whoever made the booking.
- The bonus is $50 once per original lost call, when a rebooked call shows. "Showed" uses the existing source order: #closer-eod, then Zoom.
- If the rebooked call no-shows, the same case reopens. It can earn $50 at most once.

---

## Scorecard (see `mockup/scorecard.png`)

The confirmation row stays as it is. The recovery row has two halves:

**Did the work (scored, green or red; counts toward "X of N hit"):**

| Tile | Hit when |
|---|---|
| Resched. asks | Every reschedule request that came in during his shift was called within 15 min |
| First touch | Every new case got its first touch on the day it was due |
| Daily touches | Every open case got its touch that day (days 2–5) |
| Logging | Zero recovery logging errors. An error is either of these: a rebook with no Call Confirmation Specialist activity, or an activity with no booking behind it or the wrong "Recovered from?" |

**Results (blue, information only):**
- Rebooked that day, out of the cases he worked.
- Recovered calls that showed that day.
- Bonus earned that day. It's marked "pending week gate" until the week is approved.

**Week-so-far strip:**
- Shows lost calls → reached → rebooked → showed, how many rebooked calls are still ahead, and the bonus so far.
- It ties his daily work to his pay without making results pass/fail.

Recovery misses join the same "Reply with why" list, labelled by type and step (for example `NO-SHOW · FIRST TOUCH`). They follow the same Reviews and Slack decision flow as confirmation misses.

Why results are blue rather than red or green: a rebook depends partly on the prospect, and 2 weeks of data is too little to set a fair target. I suggest we look at 3–4 weeks of numbers first, then decide whether rebook rate gets a target.

---

## Tracker (see `mockup/tracker-recovery.png`)

| Tab | Change |
|---|---|
| **Recovery** (new, built each night) | One row per case:<br>- the lost call (lead, advisor, original time, type, how it was found);<br>- D1–D5 touches (✓, ✗ or –, with what he did);<br>- status and rebook details (when, new call, calendar);<br>- logged in Close?;<br>- new call result, credit, bonus. |
| **Daily / Weekly** | New recovery columns to the right of the confirmation columns:<br>- effort (scored): reschedule asks in 15 min, first touches on time, daily touches done, logging errors;<br>- results: open, reached, rebooked, showed, bonus. |
| **Reviews** | Recovery misses and logging errors are added the same way as now, with a "Recovery" section label. They're decided the same way from #cc-gino. |
| **Management** | "Recovered calls that showed" comes from the Recovery tab instead of being typed in. Optional new **KPI 4**: recovery touches at 100% after excused misses. Recovery logging joins KPI 3. A new "rebooked calls still ahead" column, for information. |
| **Definitions** | Adds the recovery rules above. |
| **Call Recovery** (Sheila's tab) | Not touched. See decision 7. |
| Supabase | Two new tables, `call_confirm_recovery_cases` and `call_confirm_recovery_touches`. Creating them is DDL, so it needs Sheila's approval. The nightly standing approval already covers upserts into `call_confirm_*` tables. |

---

## Decisions needed from Sheila (and Jay where noted)

1. **When recovery counts toward the gate.** I propose showing it on the card and tracker from the start date, as practice, and adding it to the weekly gate (KPI 4) 1–2 weeks later. Alternative: fold it into KPI 1 right away.
2. **What one recovery touch is.**
   - My proposal (like a welcome call): double dial → no answer → voicemail.
   - On the first touch, also send the No-show or Cancel text.
   - No text on days 2–5.
   - A reschedule request gets the same touch, with no text (or a text?).
   - Jay to confirm.
3. **Where no-shows and cancels book: closers' round robin (pasted SOP) or the setter calendar (repo SOP, Nov 19)?** If the setter calendar: does the $50 pay when the setter intro call shows, or only when a later closer call shows?
4. **Does a 5:45 day-before cancel open a cancel recovery case?** The cancel text invites a rebook, so I'd say yes.
5. **The start date** for scoring recovery touches, e.g. Mon Nov 30 or Mon Dec 7. Before that date the work is shown, and only the bonus is counted.
6. **Should a whole-week results line go on Monday's card?** The Monday card would add last week's full recovery funnel and bonus to its usual layout.
7. **Your "Call Recovery" tab.** Keep it as your own and put the pipeline in a new "Recovery" tab (my default), or should the pipeline take it over?
8. **Pipeline stage discipline.** Closers moving the opportunity is the trigger, as the decisions log section 10 says. Should the tracker list lost calls the closer never moved (found by the Zoom backstop) as cases too? I'd say yes, flagged "found by backstop" and not scored until the closer moves the opportunity.
