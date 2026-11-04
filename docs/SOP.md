# Call Confirmation Specialist SOP

**Status:** DRAFT v0.1 for Sheila's review. Not yet shared with the specialist.
**Last updated:** 2026-10-30
**Source of truth for rules:** [`DECISIONS.md`](DECISIONS.md). If this SOP and the decisions log disagree, the decisions log wins.

Items marked **[PENDING]** are waiting on a decision; see Open Items at the bottom.

---

## 1. Your job in one sentence

Make sure every prospect booked for a closer's first discovery call **shows up**: confirm the call as soon as it's booked, keep confirming until the calendar invite is accepted, and win back anyone who no-shows, cancels or asks to reschedule.

### In scope
- **Every 45-minute discovery call booked with a closer**, through any Calendly link (`calendly.com/smb-st/emorg_startnow` is the main one). That includes calls you rebooked through recovery.
- Recovering **no-shows, cancellations and reschedule requests** on those calls.

### Out of scope
- The closers' 30-minute follow-up calls. Closers handle those.
- Inbound setter calls (a possible later expansion).
- Selling, pitching or qualifying. See section 9, "What you never do".

---

## 2. Tools and access

| Tool | What you use it for |
|---|---|
| **Close** (your own seat) | Dial, text, email, log every attempt, work your smart views |
| **Calendly** | See bookings; resend invites; rebook prospects onto closer calendars |
| **Slack** | Real-time alerts; read `#closer-eod` |
| **Zoom** (via Close) | No direct use. The system reads Zoom attendance to confirm shows. |

**Every attempt must be done and logged in Close under your own user.** Anything done outside Close (personal phone, personal email) doesn't count toward your KPIs or your bonus, because the system can't see it.

---

## 3. Your schedule

- **Shift:** 9:00am–6:00pm MT (11:00am–8:00pm ET), Monday to Friday.
- Most closer calls run on **Eastern Time**. Always check the time zone on the booking, and say the time in the **prospect's** time zone when you talk to them.

### Daily rhythm (MT)

| Time (MT) | What |
|---|---|
| 9:00 | **Start-of-shift sweep.** Clear everything that came in overnight: new bookings (first attempts), reschedule requests, cancels, yesterday's no-shows. Work **the soonest call first.** |
| 9:00–9:30 | **Today's calls:** any call today whose invite still isn't accepted gets its touch now. **[PENDING]** the rule for calls before about 1pm ET (open item 5). |
| 9:30 | **Tomorrow's calls:** run the "day-before" touch for every call tomorrow whose invite still isn't accepted. |
| All day | **Speed to lead:** new booking → first dial within **15 minutes**. **Same-day touch:** 2–3 hours before each unconfirmed call. Reschedule-request and cancel alerts are worked **immediately**. |
| Through the day | **No-show recovery** queue (yesterday's and older no-shows). |
| 5:45 | **End-of-shift check:** every attempt logged, every email that's due has gone out, smart views cleared or noted. |

---

## 4. Your queues (Close smart views)

**[PENDING]** These smart views will be built once Sheila approves the Close setup. Names are proposed.

| Smart view | What's in it | How fast |
|---|---|---|
| **CC – New Bookings** | Closer discovery calls booked that haven't had a first attempt yet | Within 15 minutes |
| **CC – Unconfirmed** | Upcoming calls whose invite isn't accepted yet | Per the cadence in section 6 |
| **CC – Reschedule Requests** | Opportunities a closer moved to `Reschedule Request` | Immediately |
| **CC – No-Shows** | Opportunities in `No Show/Cancel` that were no-shows, plus calls the system flagged as likely no-shows | Next business day |
| **CC – Cancels** | Cancelled closer calls | **[PENDING]** cadence |

Slack sends an alert for anything urgent. **The smart view is the list you're measured against**, not Slack.

---

## 5. The attempt sequence (use it every time)

Every confirmation or recovery touch follows the same sequence, **always in this order**:

```
STEP 1: DIAL (always first)
   ├─ You have a conversation → touch complete. Log it.
   └─ No answer → Step 2

STEP 2: VOICEMAIL + TEXT (right away)
   ├─ Prospect makes a behavior change → touch complete. Log it.
   └─ Nothing → Step 3 after 2 hours

STEP 3: EMAIL
   └─ Send 2 hours after the voicemail + text
      (immediately if the call is less than 2 hours away)
      → touch complete (sequence exhausted). Log it.
```

**A behavior change** is one of these three:
1. They **accept the calendar invite**.
2. They **reschedule**.
3. They **cancel**. A cancel isn't a dead end: it starts cancellation recovery (section 7D).

**A text or email that just says "Yes, I'll be there" is NOT a behavior change.** Thank them, then get the invite accepted (section 6, "Getting the invite accepted"). Keep going with the sequence until it is.

---

## 6. Confirming booked calls

### When to touch each call

| Touch | When | Skip if… |
|---|---|---|
| **1. Speed to lead** | Within **15 minutes** of the booking, during your shift. After-hours bookings: within 30 minutes of your next shift starting. | Never skipped |
| **2. Day before** | Morning of the day before the call | Invite already accepted |
| **3. Same day** | 2–3 hours before the call | Invite already accepted |
| **Unconfirmed** | After touch 3, if the invite still isn't accepted | Mark it Unconfirmed in Close and alert the closer |

If the call is booked for the same day or the next day, some touches collapse. Do touch 1, then touch 3 if there's time.

### What to say on the confirmation call

Keep it under 3 minutes. You're confirming, not selling.

1. **Greet and introduce:** "Hi [Name], it's [Your name] from SMB Deal Hunter. I'm calling about your call with [Closer] on [day] at [time, their time zone]."
2. **Confirm the time:** "Does that time still work for you?"
   - If no → rebook right there (section 7C).
3. **Get the invite accepted:** "You should have a calendar invite from us. Could you open it and click Accept while we're on the phone, so it's locked in on your calendar?"
4. **Set up the call:** "The call is on Zoom and runs about 45 minutes. Please join **from a computer**, not your phone, because [Closer] will share their screen and walk you through deals and examples."
5. **Lock it in:** "So we're all set for [day] at [time]. Does that 100% work for you?" Wait for a clear yes.
6. **Log it** (section 8).

### Getting the invite accepted

An invite that isn't accepted usually means **it isn't on their calendar**. Fix the cause:

| Problem | Fix |
|---|---|
| They can't find it | Check spam/promotions; search for "SMB Deal Hunter" or the closer's name |
| Wrong email on the booking | Correct the email on the Close contact, resend the invite to the right address, and note it |
| They use a different calendar (work vs. personal) | Resend to the email they actually use |
| They deleted it | Resend from Calendly |
| They just haven't clicked | Ask them to click Accept while you're on the phone |

**A call only counts as confirmed when the invite shows as accepted.** Verbal yeses don't count toward your confirmation rate.

---

## 7. Recovery

### 7A. Who owns what

| Situation | Closer does | You do |
|---|---|---|
| **No-show** | Owns the first 10 minutes: text at minute 2, call at minute 4, email at minute 5, "missed each other" message at minute 10. Then moves the opportunity to **`No Show/Cancel`**. | Start recovery the **next business day** |
| **Reschedule request before the call** | Moves the opportunity to **`Reschedule Request`** | Call **immediately** and rebook |
| **Call rescheduled on the calendar** | — | A Slack alert fires; run the full confirmation cadence for the new time |
| **Cancellation** | — | Start cancellation recovery (7D) |

If a closer didn't mark a call, the system checks Zoom attendance and inbound messages about 2 hours after the call, and puts likely no-shows in your **CC – No-Shows** view. Treat those exactly like closer-marked no-shows.

### 7B. No-show recovery

- **Start:** next business day.
- **Cadence:** one full attempt sequence per business day. **[PENDING]** how many days before the lead goes back to nurture (Jay).
- **What to say:** "Hi [Name], it's [Your name] from SMB Deal Hunter. We had you down for a call with [Closer] yesterday and it looks like we missed each other. No problem at all. Let's find a time that actually works. What does your week look like?"
- Never make them feel bad. The goal is the rebook.
- **Repeat no-shows:** if a closer's notes say **do not rebook** (e.g. a third no-show), don't. Log it and move on.

### 7C. Rebooking (all recovery types)

1. Find a time that works for the prospect.
2. **[PENDING]** Book with the **same closer** if possible; otherwise per Sheila's rule (open item 8).
3. Book through Calendly so the invite goes out automatically.
4. **Stay on the phone until the invite arrives and they accept it.**
5. Confirm the time in their time zone and the join-from-a-computer reminder.
6. Log the rebook (section 8). The new call goes into your normal confirmation cadence.

### 7D. Cancellation recovery

- **Trigger:** a cancel during confirmation, or a calendar cancel alert.
- **Cadence:** **[PENDING]** (Jay). Until it's set: run one full attempt sequence the same day (within 15 minutes during your shift), then follow the no-show recovery cadence.
- **What to say:** "Hi [Name], I saw your call with [Closer] got cancelled. I wanted to check in: did the time not work, or has something changed? Happy to find a better slot."
- If they're no longer interested, log the reason and stop. Never push.

### 7E. Reschedule requests

- **Trigger:** the opportunity moves to `Reschedule Request`.
- Call **immediately** and rebook (7C).

---

## 8. Logging in Close (your pay depends on this)

**[PENDING]** A dedicated **"Confirmation / Recovery" custom activity** is being proposed for Sheila's approval. Until it exists, log every attempt with Close's normal call, SMS and email logging, and add a short note in this format:

```
CC | <Confirm / No-show / Cancel / Reschedule> | Step <1 Dial / 2 VM+Text / 3 Email> | <Outcome> | Call date: <original> | New date: <if rebooked>
```

Proposed fields for the custom activity:

| Field | Values |
|---|---|
| Type | Confirmation, No-show recovery, Cancel recovery, Reschedule |
| Step reached | Dial – conversation, VM + text, Email |
| Outcome | Invite accepted, Rebooked, Cancelled, Rescheduled, No response, Not interested, Do not rebook, Wrong number/email fixed |
| Original call date/time | date-time |
| New call date/time | date-time (if rebooked) |
| Notes | free text |

**Rules**
- **One log per attempt, at the time you make it.** Don't batch-log at the end of the day.
- Log it **before** moving to the next prospect.
- If it isn't logged, it didn't happen: it doesn't count for the 100% gate or the $50.

---

## 9. What you never do

- **Don't pitch or sell.** Don't explain the program, deal sourcing, consulting or results. If they ask: "Great question. That's exactly what [Closer] will walk you through on the call."
- **Don't discuss price, fees, payment plans, rebates or discounts.** Never mention a "$10K rebate", a discount, or rolling the fee into a loan.
- **Don't qualify or disqualify** anyone. If something sounds like a red flag (e.g. they say they don't have the funds), note it for the closer and still confirm the call.
- **Don't give advice** on their acquisition search.
- **Don't rebook** a lead whose closer notes say not to.
- **Don't contact** anyone in the `DNC – Do Not Contact` status.
- **Don't work outside Close.** No personal phone, personal email or texts from other apps.

---

## 10. How you're measured and paid

### KPIs

| KPI | Target | Definition |
|---|---|---|
| **Attempt coverage (the gate)** | **100%** every week | Every booked closer discovery call gets its full attempt sequence at each required touch |
| **Speed to lead** | **≤ 15 minutes** | From booking to your first dial (during your shift) |
| **Confirmation rate** | **~80%** | Booked calls where the invite was **accepted** ÷ all booked closer discovery calls |
| **Show rate** | Tracked | Closer discovery-call show rate, using the team's cutoff rules (below) |
| **Recovered shows** | — | No-shows, cancels and reschedules you recovered that showed |

### Pay

| Item | Amount |
|---|---|
| Base | **$2,000 / month** |
| Recovery bonus | **$50 per recovered call that actually shows** |

- **What counts as recovered:** a no-show, cancel or reschedule where **you made logged contact in Close** after the call was lost and before it was rebooked. It counts whoever clicked "book", even if the prospect rebooked themselves after your outreach.
- **Any** cancel counts, however early.
- **$50 once per lost call.** If the same lead no-shows again and you recover them again, you're still paid $50 once, when they finally show.
- **No time limit** on when the recovered call shows.
- **The gate is weekly (Monday–Sunday).** If even one booked call that week misses its required attempt, **you don't get that week's recovery bonuses**. Your base isn't affected.
- **Bonuses are calculated weekly and paid monthly** with your base. Sheila and Jay approve every payout.
- **Ramp:** during your training period, recovered shows earn $50 **without the gate**. The date the gate starts counting will be confirmed after you join.

### How a "show" is decided

1. The closer's EOD report in `#closer-eod`.
2. The EOD Tracker sheet.
3. If those disagree or are unclear → Sheila reviews.

The system also checks Zoom: a call counts as held only if **the prospect actually joined** (not just the closer waiting in the room).

### Show-rate counting rules (for context)

The cutoff is **12:00am on the day of the call**.

| What happened | Counts as scheduled? | Result |
|---|---|---|
| Cancelled before the day of the call | No | Removed |
| Cancelled on the day of the call | Yes | **No-show** |
| Rescheduled before the day of the call | No | Removed |
| Rescheduled on the day, before the call time | No | Removed |
| Rescheduled after the call time | Yes | **No-show** |
| Didn't show | Yes | **No-show** |

So the **same-day touch matters**: a same-day cancel is a no-show, but a same-day reschedule made before the call isn't. If a prospect can't make it, getting them to **reschedule before the call time** protects the closer's show rate.

---

## 11. Escalation

| Situation | What to do |
|---|---|
| Prospect angry or asks to stop contact | Apologize, stop, log "Do not contact", tell Sheila |
| Prospect asks sales questions | Defer to the closer (section 9) and note the question for them |
| The closer isn't available at any time that works | **[PENDING]** (open item 8) |
| A tool isn't working (Close dialer, Calendly) | Post in **[PENDING: Slack channel]** and keep working the queue another way |
| You can't do a required attempt (e.g. sick) | Tell Sheila **before** it's missed |

---

## 12. Templates

All templates are **drafts** for Sheila to edit. Use the prospect's time zone.

**Voicemail (confirmation)**
> Hi [Name], it's [Your name] from SMB Deal Hunter. Just confirming your call with [Closer] on [day] at [time]. I'll text you the details. Please accept the calendar invite so it's on your calendar. Talk soon.

**Text (confirmation)**
> Hi [Name], [Your name] from SMB Deal Hunter. Your call with [Closer] is [day] at [time] [TZ] on Zoom. Please accept the calendar invite so it's on your calendar, and join from a computer, since [Closer] will share their screen. Reply here if you need a different time.

**Email (confirmation)**
> Subject: Your call with [Closer] on [day]
>
> Hi [Name],
>
> Just confirming your call with [Closer] on **[day] at [time] [TZ]** (about 45 minutes, on Zoom).
>
> Two quick things:
> 1. **Please accept the calendar invite** so it's on your calendar. Can't find it? Check spam, or reply and I'll resend it.
> 2. **Join from a computer**, since [Closer] will share their screen.
>
> Need a different time? Just reply and I'll find one that works.
>
> [Your name]
> SMB Deal Hunter

**Text (no-show recovery)**
> Hi [Name], [Your name] from SMB Deal Hunter. Looks like we missed each other for your call with [Closer]. No worries! Want me to find a new time this week? Reply with a day that works.

**Text (cancel recovery)**
> Hi [Name], [Your name] from SMB Deal Hunter. I saw your call with [Closer] was cancelled. If it was just the timing, I'm happy to find a better slot. What works for you?

---

## Open items for Sheila

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **Cancellation recovery cadence** | Sheila → Jay | Section 7D (an interim rule is in place) |
| 2 | **How long no-show recovery runs** before the lead goes back to nurture | Sheila → Jay | Section 7B |
| 3 | **Date the weekly gate starts counting fully** | Sheila, after he joins | Section 10 |
| 4 | **Approve the Close setup:** the "Confirmation / Recovery" custom activity, 5 smart views, and his Close seat | Sheila (approval) → Claude builds | Sections 4 and 8 |
| 5 | **Early ET calls:** his shift starts at 11am ET, so the "2–3 hours before" touch is impossible for calls before about 1pm ET. Proposed: the day-before touch plus a touch first thing in his shift. | Sheila to confirm | Sections 3 and 6 |
| 6 | **EOD discipline:** every closer submits EODs **through Nero only**. Tyler's plain-text Oct 29 EOD never reached the EOD Tracker. | Sheila → closers | Show accuracy and payout |
| 7 | **Nero corrections to the sheet:** Slack corrections (e.g. VeJohn, Oct 29) don't update the EOD Tracker row. Can Nero write corrections back? | Sheila → Nero's owner | Show accuracy |
| 8 | **Rebooking rules:** same closer only, or any closer if theirs is full? What if no closer has a slot that works? | Sheila | Section 7C |
| 9 | **Texting channel:** Close SMS, or iMessage via Project Blue (there's an existing "Send IMessage" activity)? | Sheila | Sections 5 and 12 |
| 10 | **Weekend bookings and calls:** his shift is Mon–Fri. Who confirms a call booked Friday night for Saturday, or Monday morning before 11am ET? | Sheila | Sections 3 and 6 |
| 11 | **Slack:** which channel do his alerts post to, and where does he escalate tool problems? | Sheila | Sections 4 and 11 |
| 12 | **Templates:** review and edit the voicemail, text and email wording | Sheila | Section 12 |
| 13 | **Service account access** to the EOD Tracker for the automated reconciliation (the email address will come later) | Sheila (when we build it) | Payout automation |
