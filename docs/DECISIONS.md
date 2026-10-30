# Call Confirmation Center: Decisions Log

The source of truth for every decision about the Call Confirmation Specialist role. The SOP, the Close setup, the Zaps and the payout code all follow this file. If anything conflicts with it, this file wins until Sheila changes it.

Last updated: 2026-10-30

---

## 1. Role and scope

- **Role:** Call Confirmation Specialist. A dedicated confirmation-and-recovery role, separate from inbound and outbound setting.
- **In scope (as of Oct 27):**
  - Confirm **all booked closer calls**.
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
| No-show | The closer owns the first 10 minutes: text at minute 2, call at minute 4, email at minute 5, "missed each other" at minute 10. Then the closer moves the lead to the **no-show** stage in Close. | Follow up the **next business day** from the smart view or Slack alert. |
| Reschedule request (before the call) | The closer moves the lead to the **reschedule-request** stage in Close | Call **immediately** to rebook |
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
2. **EOD Tracker** Google Sheet (`11PnemLh8wDT-baqbYBcW3cw0zv4vl82J7NumHTh7dCc`).
3. If those two don't settle it → **flag to Sheila**, then check Close outcomes, the calendar and the closer sheet.

Nero's `Needs confirmation` / `Provisional report` markers count as unresolved and are flagged.

## 10. Closer reporting and the backstop

- Closers must move the lead to the **no-show** or **reschedule-request** stage in Close. This will be enforced.
- **Backstop check, 2 hours after each closer call ends:**
  1. A Zoom recording on the Close record of **10+ minutes** means the call happened.
  2. If there's no qualifying recording: look for an inbound email or text asking to cancel or reschedule.
  3. If neither is found, and the closer hasn't marked the lead: flag it and add the lead to the specialist's smart view.

## 11. Systems

- **Queue:** Close smart views are the source of truth, one per workflow. Slack carries alerts.
- **Platform:** hybrid.
  - Zapier handles real-time triggers.
  - Code in this repo handles daily reconciliation and the payout report, with tests and an audit trail.
- **Where bookings originate:** to be checked by Claude, read-only (Calendly, Close meetings or Google Calendar).
- **Close guardrails:** never delete or merge anything. Every write needs Sheila's explicit approval of the exact change.

## 12. Open items

| # | Item | Owner |
|---|---|---|
| 1 | Cancellation recovery cadence | Sheila → Jay |
| 2 | How long no-show recovery runs before nurture | Sheila → Jay |
| 3 | Date the gate starts counting fully | Sheila, after he joins |
| 4 | Where bookings originate, and which event types are closer calls | Claude (read-only check) |
| 5 | Whether recent EOD Tracker rows fill the per-lead columns | Claude (read-only check) |
| 6 | Shift is 11am–8pm ET, so the "2–3 hours before" touch is impossible for ET calls before about 1pm. Proposal: those calls get the day-before touch plus the start of his shift. | Sheila to confirm |
