# Call Confirmation Center: Decisions Log

The source of truth for every decision about the Call Confirmation Specialist role. The SOP, the Close setup, the Zaps and the payout code all follow this file. If anything conflicts with it, this file wins until Sheila changes it.

Last updated: 2026-11-13 (rev 3). **Section 0 is the newest and overrides anything older below it.**

---

## 0. Updates Nov 10–13, 2026 (rev 3): live operation and the tracker

Gino Binoy started as Call Confirmation Specialist on **Tue Nov 10, 2026**. These decisions came from Sheila (with Jay) in the tracker build session and in #cc-gino. Where they differ from sections 1–12, this section wins.

### 0.1 Scope and cadence (replaces sections 1 and 6 where they differ)
- **Who he calls:** only discovery calls booked directly with an Enrollment Advisor from the Typeform (the direct discovery Calendly event type). Skip S2C (setter-booked) calls and Enrollment Advisor follow-ups. See [`SOP.md`](SOP.md).
- **Three checkpoints per call:**
  1. **Welcome call.**
     - Booked during his shift: first dial within 15 min.
     - Booked overnight: first dial within 30 min of his next shift starting.
     - Not needed if the invite was already accepted when it was due.
  2. **Day-before call**, if the invite still isn't accepted.
  3. **5:45pm MT day-before cancel**, if still not accepted by then.
- **The 5:45 cancel:**
  - Never cancel on the day of the call.
  - Never cancel a booking made that same day.
  - Only cancel next-day calls that are still unaccepted after his calls, voicemails and texts.
  - Bookings made after 5:45pm MT the day before are exempt.
- **Fridays:** the day-before call and 5:45 cancel cover **Saturday calls only**. Sunday and Monday calls have no day-before call or 5:45 cancel.
- **No touch 2–3 hours before the call.** The SOP doesn't include one, which closes open item 4.
- **Closer or setter already confirmed:** he doesn't call, and logs Closer Confirmed / Setter Confirmed. If they book again and the closer didn't reach them, it's a fresh booking.
- **Every touch:** double dial → no answer → voicemail + text. Email is no longer part of the sequence (section 3).
- **Steps he can't do aren't misses:** no voicemail option, a full mailbox, a text that won't send.
- **Only what was in his queue counts.** A call counts if it reached him through the #call-confirmation Slack alert or the Close smart views. Calls that never reached him don't count against him.

### 0.2 Confirmed and logging
- **Confirmed = invite accepted.** This hasn't changed.
  - Exceptions are approved case by case by Sheila or Jay, in #cc-gino or directly. Examples so far: a spoken confirmation when the prospect's calendar couldn't accept (Outlook), a same-day booking confirmed by text, and the Nov 12 calendar outage.
- **Confirmed by text (Sheila, Nov 13):** if the prospect texts that they'll be on the call (e.g. "See you Friday!"), that counts as confirmed from then on.
  - No day-before call or 5:45 cancel is needed after it.
  - A question, a thanks on its own, a reaction or a reschedule request doesn't count.
  - The SOP still says "Nothing else counts, not even a friendly reply to their Advisor's text"; that line needs updating to match.
- **Call Confirmation field:** options 1–9, plus Closer Confirmed and Setter Confirmed. The new options are:
  - 8 = cancelled before he reached them;
  - 9 = accepted before he reached them.
- **Lead status:** he changes Needs Confirmation → Confirmed by hand. There's no automation (Jay, Nov 13).
- **Logging check:** whenever he records an invite as accepted, the tracker checks it against Close's calendar response emails at that moment.
  - What counts as recording it accepted: field 1, 3 or 9; the "Confirmed and Accepted" outcome; or moving the lead to Confirmed.
  - If the invite wasn't accepted at that moment, his call transcript is read. A prospect who confirmed and had a technical problem accepting is a valid exception.
  - Anything else is a logging error, and Sheila and Jay judge it.

### 0.3 Weekly KPIs and bonus (replaces the gate in sections 2–3)
**Not in the SOP yet; Sheila is keeping them out until they're final.** The tracker uses these for now:
- **Week:** Monday to Sunday. The KPIs count from the **week of Nov 23**. Earlier weeks are ramp: recovered shows pay $50 with no KPI check.
- **KPI 1:** 100% of checkpoints finished, after excused misses.
- **KPI 2:** at least 85% of during-shift welcome calls first dialed within 15 minutes. The margin allows for meetings.
- **KPI 3:** zero logging errors that Sheila or Jay count as a miss. Every logging error is flagged for their decision.
- **Bonus** = recovered calls that showed × $50. Sheila and Jay both sign off each week on the tracker's Management tab.

### 0.4 Who decides what counts
- **Reviews tab:** every miss and logging error is listed for Sheila or Jay to mark "Counts as a miss" or "Excused". A blank decision on a miss counts as a miss; a blank on a logging error holds the week at "Waiting on review".
- **Approvals in #cc-gino count.** If Sheila or Jay already approved a specific lead there, the tracker marks that lead's rows Excused, with a link, and never overwrites a decision.
- **General rules from #cc-gino are hints only.** They're noted on the row, and Sheila and Jay still decide.

### 0.5 Tracker and data
- **Tracker:** the Google Sheet "Call Confirmation Tracker (Gino)" (`1R4l1Szm7cxfu70sBxGpWsJncsu0mlyFPiwatJg6Kdsk`).
  - Tabs: Management, Reviews, Calls, Daily, Weekly, Definitions, Data Sources.
  - Sheila also keeps two tabs of her own, "Call Confirmation>>" and "Call Recovery" (for later).
- **Nightly update:** 8:00pm MT every day, weekends included. Nothing is due on weekends, but his activity is recorded.
  - It runs as an unattended scheduled task following [`tracker/RUNBOOK.md`](../tracker/RUNBOOK.md).
  - On Sundays it posts a review reminder in #cc-gino for Sheila and Jay.
  - Management!A5 shows when the tracker was last updated, so stale data is obvious.
- **Where the data comes from:** the #call-confirmation Slack alerts and Close smart views first; Calendly and Close fill the gaps.
- **"Showed":** #closer-eod first, then Zoom attendance (section 9 still applies). In 3–5 days Sheila will confirm whether this is the right source.
- **History:** everything each run reads is kept in Supabase setter-data, in the `call_confirm_*` tables (schema: [`tracker/supabase/call_confirmation_schema.sql`](../tracker/supabase/call_confirmation_schema.sql)).
  - That covers Close, Calendly, Slack, the tracker's rows, Sheila's and Jay's decisions, and a copy of every tab after each run.
  - The nightly run only adds or updates rows; it never deletes.
- **Standing approvals** for the unattended run are listed at the top of the runbook.

### 0.6 Still open
| # | Item | Owner |
|---|---|---|
| A | KPIs and bonus wording for the SOP | Sheila |
| B | Lead status rule: does "unreachable, then accepted before contact" also go to Confirmed? (Gino's restatement only got a ✓ reaction) | Jay |
| C | Invites that arrive late: whether to widen the 15-minute speed-to-lead window | Sheila |
| D | Confirm the "showed" source (#closer-eod vs. the EOD Tracker vs. the Sales Tracker) | Sheila, around Nov 16–18 |
| E | The Call Recovery tab and recovery tracking; the daily scorecard | Later |

---

## 1. Role and scope

- **Role:** Call Confirmation Specialist. A dedicated confirmation-and-recovery role, separate from inbound and outbound setting.
- **In scope (as of Oct 27):**
  - Confirm **all booked closer calls**: any **45-minute** meeting booked with someone on the closer roster, whichever Calendly link was used (`emorg_startnow` is the main one, but there are dozens of 45-minute closer event types). This includes rebooks from recovery.
  - **Excluded:** the closers' 30-minute follow-up calls, which closers manage themselves.
  - Recover **no-shows, reschedules and cancellations**.
- **Out of scope for now:** confirming inbound setter calls. That's a later expansion.
- **Location:** Alberta, Canada (Mountain Time).
- **Shift:** 9am–6pm MT (11am–8pm ET). Monday to Friday unless changed.
- **Accounts needed:** a new Close seat, a Slack account and Calendly access.

## 2. Pay

| Item | Decision |
|---|---|
| Base | $2,000 per month for confirmation work |
| Recovery bonus | $50 per recovered set that **shows**. A rebook alone earns nothing. |
| Repeat recoveries | $50 **once** per original lost call, even if the lead needs several recoveries before showing |
| Time limit | None. The recovered call can show any time later and still pay. |
| Gate | **Weekly** 100% confirmation-attempt KPI. One missed attempt forfeits that week's recovery bonus. |
| Gate week | Monday to Sunday |
| Payout cadence | Base paid monthly. The bonus is calculated week by week against the gate and paid monthly with the base. |
| Approval | **Sheila + Jay** approve each payout report before payment |
| Ramp | Onboarding starts around Tue Nov 3. During the ramp, recovered shows earn $50 with **no gate**. The date the gate starts counting fully is **to be decided after he joins**. |

## 3. Confirmation attempt (the 100% gate)

An attempt is this sequence, always in this order:

```
1. Dial (always first)
   ├─ Conversation → attempt complete
   └─ No answer → 2
2. Voicemail + text
   ├─ Behavior change → attempt complete
   └─ None → 3 (after 2 hours)
3. Email → attempt complete (sequence exhausted)
```

- **Behavior change** = the prospect **accepts the calendar invite**, **reschedules** or **cancels**.
- A written "yes" by text or email is **not** a behavior change. The specialist still has to get the invite accepted. An unaccepted invite usually means it isn't showing on the prospect's calendar, so the specialist fixes that, resending it if needed.
- **Email timing:** 2 hours after the voicemail + text if nothing changes. Immediately if the call starts in less than 2 hours.
- **A cancel** during confirmation starts cancellation recovery right away.

## 4. Confirmed (the ~80% target)

- **Confirmed = calendar invite accepted.** Nothing else counts.
- Target confirmation rate: about 80%, measured as confirmed calls ÷ booked closer calls.

## 5. Speed to lead

- First dial within **15 minutes** of a closer call being booked, during working hours.
- Bookings outside working hours: first dial within 30 minutes of the next shift starting.

## 6. Pre-call confirmation cadence

For each booked closer call, until the invite is accepted:

1. A full attempt sequence within 15 minutes of booking.
2. A full sequence on the morning of the day before the call.
3. A full sequence 2–3 hours before the call.
4. If still not accepted, mark the call **Unconfirmed**.

## 7. Recovery

### Who earns the $50
- The specialist earns credit if they made **any contact logged in Close** after the lost call and before the rebook, **whoever did the booking**. That includes the prospect rebooking themselves through a link.
- **Every** no-show, cancel or reschedule is eligible, however early it happened.

### Triggers
| Type | Trigger | Specialist's action |
|---|---|---|
| No-show | The closer owns the first 10 minutes: text at minute 2, call at minute 4, email at minute 5, "missed each other" at minute 10. Then the closer moves the opportunity to **`No Show/Cancel`** in the Sales pipeline. | Follow up the **next business day** from the smart view or Slack alert. |
| Reschedule request (before the call) | The closer moves the opportunity to **`Reschedule Request`** in the Sales pipeline | Call **immediately** to rebook |
| Rescheduled on the calendar | A Zap alerts the specialist | Call and confirm the new time (full confirmation cadence) |
| Cancellation | A cancel caught during confirmation, or a calendar cancel | Recover |

### Pending Jay's input
- **Cancellation recovery cadence:** to be decided after Sheila checks the current closer workflow with Jay.
- **How long no-show recovery runs** before the lead goes back to nurture: pending Jay.

## 8. Show-rate counting (closer calendars)

The cutoff is **12:00 a.m. on the day of the call**.

| Event | Timing | Counts as scheduled? | Outcome |
|---|---|---|---|
| Cancel | Before the cutoff (a day or more ahead) | No, removed | — |
| Cancel | After the cutoff (same day) | **Yes** | **No-show** |
| Reschedule | Before the cutoff | No, removed | — |
| Reschedule | Same day, **before** the call time | No, removed | — |
| Reschedule | **After** the original call time | **Yes** | **No-show** |
| No-show | — | Yes | No-show |

- Reschedules are logged against the **lead record in Close**, not the closer.
- Worked example (Owen, 5 calls on 10/1, 4 held): a cancel on 9/30 → 4 scheduled / 4 live. A cancel on 10/1 → 5 / 4. A reschedule on 9/30 → 4 / 4. A reschedule on 10/1 before the call → 4 / 4. A no-show that reschedules after the call time → 5 / 4.
- This show rate is the main measure of the specialist's performance.

> Note: the separate pre-call behavior taxonomy (3+ days' notice = don't count) is **not** used for the bonus. Every recovery type is bonus-eligible (section 7).

## 9. Source of truth for "showed"

In order:
1. **`#closer-eod`** in Slack (C06RE8S1L4V). Nero's per-lead EOD lines link to Close leads.
2. **EOD Tracker** Google Sheet (`11PnemLh8wDT-baqbYBcW3cw0zv4vl82J7NumHTh7dCc`). Columns W–AB (`follow_ups`, `showed_leads`, `no_showed_leads`, `cancelled_leads`, `rescheduled_leads`, `follow_up_leads`) list Close lead links, so matching is by lead ID. Rows that Nero marks `Needs confirmation` leave the counts blank, and Slack corrections don't flow back to the sheet.
3. If those two don't settle it → **flag to Sheila**, then check Close outcomes, the calendar and the closer sheet.

Nero's `Needs confirmation` / `Provisional report` markers count as unresolved and are flagged.

## 10. Closer reporting and the backstop

- Closers must move the opportunity to **`No Show/Cancel`** or **`Reschedule Request`** in the Sales pipeline. This will be enforced. `No Show/Cancel` is one combined stage, so no-show vs. cancel is decided by timing (section 8).
- **Backstop check, 2 hours after each closer call ends:**
  1. **Showed = the prospect joined the Zoom.** Read `meeting.integrations` (`integration_name == "zoom"`) on the Close meeting. If anyone other than the closer and the closer's notetaker appears in `integration_data.participants`, the call happened. Zoom duration is reported as context only and never decides on its own: closers wait 10–16 minutes in the room when a prospect no-shows. On Oct 29, three EOD no-shows had 12–16 minutes of Zoom time.
  2. If there's no Zoom data, or the prospect didn't join: look for an inbound email or text asking to cancel or reschedule.
  3. If neither is found, and the closer hasn't marked the lead: flag it and add the lead to the specialist's smart view.

## 11. Systems

- **Queue:** Close smart views are the source of truth, one per workflow. Slack carries alerts.
- **Platform:** hybrid.
  - Zapier handles real-time triggers.
  - Code in this repo handles daily reconciliation and the payout report, with tests and an audit trail.
- **Bookings:** Calendly, mostly through `calendly.com/smb-st/emorg_startnow`. Calendly bookings sync to Close as meetings; a 45-minute duration identifies closer calls. Some meetings appear twice in Close, so the code dedupes them.
- **Close meeting fields:** `duration` is the scheduled length in seconds. `actual_duration` is Close's own call time and is often empty; it is not the Zoom time. Zoom data is under `integrations[].integration_data` (`duration` in minutes, `start_time`, `end_time`, `participants`).
- **Sales pipeline stages** (`pipe_6BtcTllrXJwFF7nSvcRrLu`): Discovery Call Scheduled, Next 7 Days, In Month Closing, Long Term w/ Intention, Long Term No Timeline, Long Term Farm, Split Pay/Deposit, Offer Not Presented, **Reschedule Request**, **No Show/Cancel**, WON, LOST.
- **Close guardrails:** never delete or merge anything. Every write needs Sheila's explicit approval of the exact change.

## 12. Open items

| # | Item | Owner |
|---|---|---|
| 1 | Cancellation recovery cadence | Sheila → Jay |
| 2 | How long no-show recovery runs before nurture | Sheila → Jay |
| 3 | Date the gate starts counting fully | Sheila, after he joins |
| 4 | Shift is 11am–8pm ET, so the "2–3 hours before" touch is impossible for ET calls before about 1pm. Proposal: those calls get the day-before touch plus the start of his shift. | Sheila to confirm |
| 5 | Closers must submit EODs through Nero only; plain-text EODs (Tyler, Oct 29) never reach the EOD Tracker | Sheila → closers |
| 6 | Slack corrections don't update the EOD Tracker row (VeJohn, Oct 29). Can Nero write corrections back? | Sheila → Nero's owner |

Full open-items list, including SOP-level items: see `SOP.md`.
