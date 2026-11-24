# Proposal: call recovery on Gino's scorecard and tracker

Status: **draft for Sheila's review (rev 2, Nov 24).** Nothing here is built or live. It stays on a branch until Sheila approves it. When she does, the build updates `docs/DECISIONS.md`, `docs/SOP.md`, the pipeline, the scorecard and the runbook.

Sources:
- Sheila's updated Call Confirmation Quick Guide (pasted Nov 24, with the new Call Recovery section).
- Her answers in the review session (Nov 23–24).
- Close as of Nov 24.

Mockups (sample data, made-up names):
- `mockup/scorecard.png`: the Tue–Fri card with the recovery row.
- `mockup/scorecard-monday.png`: the Monday card. It shows Friday, plus last week's full recovery numbers.
- `mockup/tracker-recovery.png`: the recovery tab, the new Daily/Weekly columns, and the Management changes. **This is rev 1. It still shows the old D1–D5 rules and a gate; it will be redrawn to match the rules below.**

---

## Rules (decided with Sheila, Nov 23–24)

### Pay: recovery never gates anything
- Recovery is Gino's discretionary effort for the bonus. **Nothing in recovery affects his base pay, his base KPIs or whether he gets the bonus.**
- **$50 per recovered call that shows.** This applies to no-shows, cancels and reschedule requests alike, and counts recoveries from **Nov 24** on, once the routine is turned on.
- Recovery touches are tracked and shown as a KPI. That KPI is **information only**.

### Where recoveries book
- Every recovery books on the **closers' round robin**, `https://calendly.com/smb-st/sdrb_c2_startnow`.
- The repo's old SOP said "setter calendar for no-shows and cancels". That is out of date.

### When a row is added (a "case")
- **A row is added when a lead lands in recovery.** That means one of these lead statuses:
  - `No Show - Recovery`
  - `Cancelled - Recovery`
  - `Reschedule Request - Recovery`
- **The 5:45 day-before cancels count** as lost calls to recover.
- **Backlog leads** (the Backlog smart view) get a row the first time Gino touches one.
- **Lost calls found only by the Zoom backstop** (the closer never moved them in the pipeline):
  - They appear on the tracker and are flagged.
  - They're **not scored**, because they never reached Gino's smart views or Slack.
  - Gino can label them in Close and work them. A rebook that shows still earns the $50.

### The 5-business-day sequence starts at his first attempt
- The clock starts at **Gino's first attempt**, not when the lead lands in recovery.

| Day | Due | Call Recovery field |
|---|---|---|
| 1 | Call → double dial → recovery voicemail + the Day 1 text for the type (no-show, cancel or reschedule request) | Day 1 Recovery - No Pickup, Double Dial, VM, Text |
| 2 | Call only | Day 2 Recovery - No Pickup |
| 3 | Call + Day 3 voicemail + Day 3 text | Day 3 Recovery - No Pickup (see note) |
| 4 | Call only | Day 4 Recovery - No Pickup |
| 5 | Call + breakup voicemail + breakup text, then stop | Day 5 Recovery - No Pickup, Double Dial, VM, Text |

- **The sequence ends early when:**
  - he rebooks the lead (field = Rebooked);
  - the lead says "not interested" or "already bought";
  - he sets a callback task.
- **Closer exception:** if the closer is already rescheduling the lead, Gino stays out, and those days aren't counted against him. He takes over if the closer sent their own calendar link and the lead hasn't replied in 24 hours.
- **Reschedule requests** are called within 15 minutes if they come in during his shift, as the SOP's "right away" (open item A).
- After a rebook, the new call is a **new booking** and goes through normal confirmation, including the day-before 5:45 cancel.

### Credit for a rebook
Gino earns the credit only if **all** of these hold:
1. He touched the lead after it entered recovery, and before the rebook.
2. The rebook is on the closers' round robin, not a closer's personal calendar.
3. **Gino is the scheduler on the Calendly event.** He books the lead in himself and never sends the link.
4. Nobody else tried to rebook the lead in between.

The bonus pays only when the lead **shows** to that rebooked call. "Showed" uses the existing source order (#closer-eod, then Zoom).
- $50 is paid **once per original lost call**.
- At most 2 rebooks per person. If the rebooked call no-shows, the same case reopens.

Open item B below covers how the tracker proves #3.

---

## Scorecard

**Tue–Fri card** (`mockup/scorecard.png`)
- **The confirmation row stays as it is.** The "X of 7 hit" pill counts **confirmation only**.
- **The recovery row has two halves.**
  - **Did the steps** (green or red, information only). Each tile is a hit when:
    - **Resched. asks:** reschedule requests during his shift were called within 15 minutes.
    - **Day 1 touch:** every Day 1 had the full sequence (call, double dial, voicemail, text).
    - **Days 2–5:** every case due a touch that day got the right one.
    - **Logging:** no recovery logging errors. Those are:
      - the Call Recovery field doesn't match what he did;
      - a rebook with no Call Confirmation Specialist activity;
      - an activity with no booking behind it.
  - **Results that day** (blue). Each counts events that happened **on the scored day**:
    - **Rebooked:** leads Gino booked in Calendly that day, whenever they were lost.
    - **Showed:** recovered calls that showed that day. They were rebooked on an earlier day, so this is the payoff of past work.
    - **Bonus:** those shows × $50.
- **"This week so far" line:** the lost calls opened this week and how far they've got, plus this week's bonus. The bonus counts by the week the recovered call shows.
- **Recovery misses** go in the same "Reply with why" list and the same Slack decision flow.

**Monday card** (`mockup/scorecard-monday.png`)
- It covers Friday as usual, plus a **"Last week's call recovery"** box. The box has:
  - **The funnel of last week's lost calls only:** lost → worked → reached → rebooked → showed.
  - **The bonus:** every recovered call that showed last week, whenever it was lost, split into this week's and backlog.
  - **Still ahead:** rebooked calls still to come, and what they could earn.
  - A **by-type** line, **recovery touches %** (information only), **backlog** worked/rebooked/showed, and **found by Zoom, not moved by the closer**.

---

## Tracker

| Tab | Change |
|---|---|
| **Recovery** (new, built each night) | One row per case:<br>- the lost call (lead, advisor, original time, type, how it was found);<br>- first attempt and Days 1–5 (due vs done, what he did, the field value he logged);<br>- status and end reason;<br>- rebook (when, the new call, calendar, scheduler = Gino?, logged?);<br>- the new call's result, credit, bonus and bonus week. |
| **Daily / Weekly** | Recovery columns to the right of the confirmation columns: the steps (information only) and the results. |
| **Reviews** | Recovery misses and logging errors, with a "Recovery" label, decided the same way from #cc-gino. They are never part of the bonus check. |
| **Management** | "Recovered calls that showed" is counted from the Recovery tab instead of typed in. Recovery stays out of the KPIs and the "Compliant" check. The bonus = recovered shows × $50, approved weekly by Sheila and Jay as now. A "rebooked calls still ahead" column is added for information. |
| **Definitions** | Adds the rules above. |
| Supabase | Two new tables, `call_confirm_recovery_cases` and `call_confirm_recovery_touches`. Creating them is DDL, so it needs Sheila's approval. |

**Question 7, the empty "Call Recovery" tab.** The tracker already has a tab called "Call Recovery". It's empty, like a section divider, the same as "Call Confirmation>>". **Proposal:**
- Rename it **"Call Recovery>>"** so it works as a divider.
- Put the new recovery tab(s) right after it.

Sheila decides.

---

## Still open

| # | Item | Proposed |
|---|---|---|
| A | Reschedule request "right away" | Within 15 minutes during his shift; first 30 minutes of the next shift if it comes in overnight |
| B | **Proving Gino was the scheduler in Calendly** | To check: whether Calendly's booking data names who booked on the invitee's behalf. If it doesn't, the fallback is "Gino had a live call or text with the lead in Close in the minutes before the booking was created". Sheila to approve whichever proves reliable. |
| C | Days 2–5: one dial or a double dial? | One dial, unless the SOP says otherwise |
| D | Close field fixes (Sheila's call, nothing changed) | Rename "Day 3 Recovery - No Pickup" to include VM + Text. Add choices for "Not interested" and "Callback set", so a case can end early for the right reason. |
| E | "Call Recovery - Follow-up" smart view | Add a "not called today" filter, or sort by last call, so he doesn't call anyone twice or skip anyone |
| F | Call Recovery tab naming (question 7 above) | Rename it to a divider; new tabs go after it |
