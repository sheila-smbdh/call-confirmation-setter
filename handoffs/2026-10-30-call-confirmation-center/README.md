# Handoff: Call Confirmation Center setup

**From:** Sheila Xu's Claude Code session, 2026-10-30
**To:** Jay's Claude (Cowork / chat), with Jay in the chat
**Mission:** Help Jay finish the Call Confirmation Specialist's SOP with Sheila, close the open decisions Jay owns, and move the setup forward (Close setup, Zaps, payout tracking) so the new specialist can start the week of Nov 2.

Read this whole file first. It is self-contained: every decision made so far is written out below. The links in section 2 are extras. Use them if this surface can open them; say so if it can't.

---

## 1. What this is

SMB Deal Hunter is hiring a **Call Confirmation Specialist**. The role does confirmation and recovery only, separate from inbound and outbound setting. He confirms every 45-minute discovery call booked with a closer, and wins back no-shows, cancellations and reschedule requests on those calls. He's based in Alberta (Mountain Time). The offer goes out Monday Nov 2, he starts around Tue Nov 3, and he ramps through that week. Full counting starts later, on a date Sheila sets after he joins.

Sheila worked through the role with Claude on Oct 29–30. Together they locked the scope, the pay plan, the attempt rules, the show-rate counting rules and the sources of truth. Claude checked these against live data (read-only): Close, Calendly, Slack `#closer-eod` and the EOD Tracker sheet. It then wrote a draft SOP as a shared, editable Claude doc for Sheila and Jay to finish together.

What remains: answer the open decisions (two are Jay's), finish the SOP wording, then build the Close setup, the Slack alerts (Zapier) and the reconciliation and payout tracking. Building the tracking code needs Claude Code with the repo. This chat surface can help decide, draft and review, but it can't run that code.

## 2. Where everything lives

| Resource | What it is | Read in full? |
|---|---|---|
| **This file** | Every decision, blocker and next step | Yes |
| **SOP doc:** https://claude.ai/artifact/KS1EBc5RyDp7HiG8Xwh1MB | The draft SOP (v0.1) Sheila and Jay are editing together. It ends with an **Open items** table that has a status dropdown and an answer column. | Yes, if this surface can open it. Sheila has to share it with Jay first. |
| **Repo:** `sheila-smbdh/call-confirmation-setter` on GitHub | `docs/DECISIONS.md` is the source-of-truth log (merged on `main`). `docs/SOP.md` (markdown draft) and this handoff are on branch `claude/youthful-ptolemy-wsl2u7`. | No. Everything that matters is copied into this file. Jay may not have repo access. |
| Slack `#closer-eod` (C06RE8S1L4V) | Nero bot posts each closer's EOD, with per-lead Close links | Only if checking a specific show |
| EOD Tracker sheet (`11PnemLh8wDT-baqbYBcW3cw0zv4vl82J7NumHTh7dCc`) | One row per closer per day; columns W–AB list showed, no-show, cancel and reschedule leads as Close links | No |
| Close Sales pipeline (`pipe_6BtcTllrXJwFF7nSvcRrLu`) | Where closers mark `No Show/Cancel` and `Reschedule Request` | No |

## 3. Decisions locked (do not re-litigate)

These are settled. Raise a concern only if Jay asks for one. Don't reopen them on your own.

**Role and scope**
- Confirm **every 45-minute discovery call booked with a closer**, through any Calendly link (`calendly.com/smb-st/emorg_startnow` is the main one; there are dozens of 45-minute closer event types). Rebooks from recovery are included.
- **Excluded:** closers' 30-minute follow-up calls (closers handle those) and inbound setter calls (a possible later expansion).
- Shift: **9am–6pm MT (11am–8pm ET), Monday to Friday.**
- Accounts he needs: a new Close seat, Slack, Calendly access.

**Pay**
- **$2,000 per month base.** Plus **$50 per recovered call that actually shows** (a rebook alone earns nothing).
- $50 **once** per original lost call, even if the lead needs several recoveries before showing. **No time limit** on when the recovered call shows.
- **The gate is weekly (Mon–Sun), at 100% confirmation attempts.** One booked call that misses its required attempt forfeits that week's recovery bonuses. The base isn't affected.
- The bonus is calculated weekly and paid monthly with the base. **Sheila and Jay both approve each payout.**
- Ramp: recovered shows earn $50 with no gate. The date the gate starts counting is decided after he joins.

**Recovery credit**
- He gets the $50 if he made **any contact logged in Close** after the call was lost and before it was rebooked, **whoever did the booking**. That includes the prospect rebooking themselves after his outreach.
- **Every** no-show, cancel or reschedule is eligible, however early it happened.

**The attempt sequence** (every touch, always in this order)
1. **Dial.** A conversation means the touch is complete.
2. No answer → **voicemail + text** right away. A behavior change means the touch is complete.
3. Nothing changes → **email 2 hours later** (immediately if the call is less than 2 hours away). The touch is complete.
- **Behavior change** = the prospect **accepts the calendar invite, reschedules, or cancels**. A written "yes, I'll be there" is NOT one; he still has to get the invite accepted. A cancel starts cancellation recovery.

**Confirmed, speed and cadence**
- **Confirmed = calendar invite accepted.** Nothing else counts. Target: about **80%** of booked closer discovery calls.
- **Speed to lead:** first dial within **15 minutes** of booking during his shift. After-hours bookings: within 30 minutes of his next shift starting.
- **Cadence until the invite is accepted:** on booking, the morning of the day before, then 2–3 hours before the call. After that, the call is marked **Unconfirmed**.

**Recovery triggers**
- **No-show:** the closer owns the first 10 minutes (text at minute 2, call at minute 4, email at minute 5, "missed each other" at minute 10), then moves the opportunity to **`No Show/Cancel`** in the Sales pipeline. The specialist follows up the **next business day**.
- **Reschedule request before the call:** the closer moves the opportunity to **`Reschedule Request`**, and the specialist calls **immediately**.
- **Rescheduled on the calendar:** a Zap alerts him, and he runs the full confirmation cadence for the new time.
- **Queue:** Close smart views are the source of truth; Slack is only for alerts. **Platform:** Zapier for real-time triggers; code in the repo for reconciliation and payout.

**Show-rate counting** (cutoff = 12:00am on the day of the call)

| What happened | Counts as scheduled? | Result |
|---|---|---|
| Cancelled before the day of the call | No | Removed |
| Cancelled on the day of the call | Yes | No-show |
| Rescheduled before the day of the call | No | Removed |
| Rescheduled on the day, before the call time | No | Removed |
| Rescheduled after the call time | Yes | No-show |
| Didn't show | Yes | No-show |

Reschedules are logged against the lead in Close, not against the closer. This show rate is the main measure of the specialist's performance.

**Source of truth for "showed"**, in order: (1) the EOD in Slack `#closer-eod`, (2) the EOD Tracker sheet, (3) if those don't settle it, **flag to Sheila**, then check Close, the calendar and the closer sheet.

**Backstop when a closer doesn't mark a call:** runs about 2 hours after the call.
- **Showed = the prospect joined the Zoom.** On the Close meeting, look at `integrations` where `integration_name == "zoom"`. If `integration_data.participants` includes anyone besides the closer and the closer's notetaker, the call happened.
- **Zoom duration never decides on its own.** On Oct 29, three calls the closers reported as no-shows (Greg Payseur, Andre White, Chase Mclelland) had 12–16 minutes of Zoom time from the closer waiting alone in the room.
- If there's no Zoom data, or the prospect didn't join: check for an inbound email or text asking to cancel or reschedule. If there's none, flag the call and add the lead to the specialist's no-show smart view.

**Close guardrails** (Sheila's standing rules, which apply to any Claude touching her Close)
- Never delete or merge anything in Close.
- Every write (creating fields, smart views, statuses, logging, sending) needs explicit approval of the exact change first.
- Reads need no approval.

## 4. Changed since this work paused

1. **The SOP moved from markdown to a shared Claude doc.** The doc (section 2) is the version to edit. The markdown `docs/SOP.md` on the repo branch is older and won't be kept in sync.
2. **The show rule changed from "Zoom 10+ minutes" to "the prospect joined the Zoom"** after the Oct 29 data check. Any older note that mentions 10 minutes is outdated.
3. **The EOD Tracker check passed:** recent rows list per-lead Close links, so matching works by lead ID. Two gaps were found (items 6 and 7 below).

## 5. Blockers and unblock paths

| # | Open item | Owner | Unblock |
|---|---|---|---|
| 1 | **Cancellation recovery cadence** (interim rule: one sequence within 15 min, then the no-show cadence) | **Jay** | Describe the current closer workflow for cancels, then pick the specialist's cadence |
| 2 | **How long no-show recovery runs** before the lead goes back to nurture | **Jay** | Pick the number of business days |
| 3 | Date the weekly gate starts counting fully | Sheila, after he joins | — |
| 4 | Approve the Close setup: a "Confirmation / Recovery" custom activity, 5 smart views, his Close seat | Sheila approves; a Claude Code session builds | Approve the spec in the SOP's *Logging* and *Queues* sections |
| 5 | **Early ET calls:** his 11am ET start makes the "2–3 hours before" touch impossible for calls before about 1pm ET. Proposed: the day-before touch plus a touch first thing in his shift. | Sheila | Confirm or change |
| 6 | **EODs through Nero only:** Tyler's plain-text Oct 29 EOD never reached the EOD Tracker | Sheila or Jay → closers | Tell closers |
| 7 | **Nero corrections to the sheet:** Slack corrections (e.g. VeJohn, Oct 29) don't update the sheet row | Sheila → Nero's owner | Ask whether Nero can write corrections back |
| 8 | **Rebooking:** same closer only, or any closer? What if no slot works? | Sheila (Jay's input useful) | Decide |
| 9 | **Texting channel:** Close SMS, or iMessage via Project Blue? | Sheila | Decide |
| 10 | **Weekend and early-Monday coverage** for bookings and calls outside his shift | Sheila (Jay's input useful) | Decide |
| 11 | **Slack channel** for his alerts and tool escalations | Sheila | Decide |
| 12 | **Template wording** (voicemail, text, email) | Sheila + Jay | Edit in the SOP doc |
| 13 | **Service-account access** to the EOD Tracker for the automated job | Sheila, when the code is built | Share the sheet with the email given then |

These match the **Open items** table at the end of the SOP doc. When a decision lands, update that table: set the status to Decided and type the answer.

## 6. First moves, in order

1. Read this file in full. Tell Jay in two or three lines what you loaded, and whether this surface can open the SOP doc link. If it can't, say so and ask Jay to have Sheila share it (or paste its contents).
2. Ask Jay which he wants to start with, as tappable options: **(a)** his two open decisions (#1 cancel cadence, #2 no-show length), **(b)** reviewing and editing the SOP doc, **(c)** the cross-team items where his input helps (#8 rebooking, #10 coverage, #12 templates).
3. For #1 and #2: ask one question at a time, with tappable options and a recommended default. Start by asking how closers handle cancels today, because the specialist's cadence should complement theirs, not duplicate it.
4. When decisions land, write them into the SOP doc's Open items table (status → Decided, answer filled in) and into the matching SOP section. If this surface can't edit the doc, give Jay the exact text to paste.
5. Building (Close custom activity and smart views, Zaps, reconciliation and payout code) happens in a Claude Code session with the repo, with Sheila approving every Close write. If Jay wants to move on it, draft the spec here and hand it to that session.

## 7. Tone

Keep it about the specialist, the closers and the numbers. Keep tool names, branches and IDs out of Jay's way unless he asks. Ask one question at a time, with tappable options and a recommended default; that's how Sheila worked through all of this and it went fast. Jay and Sheila share approval of payouts, so flag anything that changes pay math to both of them.

If this feels hard or confusing at all, please reach out to Zain. He promises he wants to hear all about it, so he can make this feel like magic. Thank you for using it!

## 8. Done means

- Every row in the SOP doc's Open items table is **Decided**, or explicitly parked with an owner and date.
- The SOP doc is final and ready to give the specialist at onboarding (week of Nov 2).
- The Close setup spec is approved by Sheila and handed to a Claude Code session to build. The Zap and reconciliation work is queued behind it.
- Sheila is told, in one plain message, which decisions Jay made and what changed in the SOP.
