# Call Confirmation Center: Decisions Log

The source of truth for every decision about the Call Confirmation Specialist role. The SOP, the Close setup, the Zaps and the payout code all follow this file. If anything conflicts with it, this file wins until Sheila changes it.

Last updated: 2026-11-27 (rev 11). **The newest section is first and overrides anything older below it** (000000000, then 00000000, then 0000000, then 000000, then 00000, then 0000, then 000, then 00, then 0).

---

## 000000000. Update Nov 27, 2026 (rev 11): Nov 25 scorecard review

From Sheila's and Jay's review of Gino's Nov 25 scorecard ([thread](https://dylanhelen.slack.com/archives/C0CG28G7TQT/p1795703917997549)), and Sheila's request to update the rules from it (Nov 27). Where a rule below is Claude's recommendation that Sheila hasn't ruled on yet, it says so.

| # | What happened (Nov 25) | Decision / rule from now on |
|---|---|---|
| — | Jay replied "N - Confirmed" to every item, including #10, where Gino admitted the miss. | **Jay's "Confirmed" means he agrees with Gino's explanation of that item.** If Gino explained why it wasn't a miss, it's excused. If Gino admitted the miss, it **counts as a miss**. "Missed" = a miss. The morning run reads Gino's reply for that number to tell which (RUNBOOK step 4b). Before Nov 27 the run read every "Confirmed" as excused; none of those earlier items was one Gino had admitted. |
| 1, 3, 4 | Colin Mitchell, Peter Mosesian: Gino was texting or emailing with the closer, who confirmed. | Excused (Jay). Existing rule (SOP, Nov 13): when the closer confirms, Gino logs **Closer Confirmed**, which stops the welcome, day-before and 5:45 checks. Nothing changes in the tracker; Gino should log it. |
| 2 | Steve Miller: follow-up call not made; confirmed by text. | Excused (Jay). **The morning run now reads the prospect's texts for follow-up calls too**, not just day-before calls, 5:45 cancels and logging errors. A text saying they'll attend stops the follow-ups from then on (rule since Nov 19). |
| 5 | Loai Hekmat: "Call Confirmation Specialist activity logged, but no new booking found." | Excused (Sheila: compliant). Close shows Gino logged the activity on Nov 25 at 4:24pm ET and **deleted it** on Nov 26 at 12:47pm ET, after the Nov 26 run flagged it, so it no longer shows on the lead. **From now on an activity with no booking is flagged only if it's still there a day later, and only if Gino logged it.** One he deletes isn't an error. |
| 6, 8 | Brian Kenney, Joe Kay: backlog leads he first called Nov 23, before tracking started. On Nov 25 he did Day 2 (double dial only) and set the field to Day 2; the tracker restarted the count at Day 1 and flagged a missing text plus a "wrong" field. | Excused (Jay). **A backlog lead he started before tracking began picks up at the day his Call Recovery field says** on his first tracked day. The Recovery tab shows the earlier days as "Before tracking (his field)". |
| 7, 9 | Dipak Joshi, Priyanka Khanna: second dial answered for 30 seconds, with a recording, no outcome logged and no transcript. Gino says he left a voicemail. | Excused (Jay). **An answered call of 30–44 seconds with no outcome logged counts as the voicemail step**, labelled "Voicemail likely (no outcome logged)". This applies to confirmation checkpoints and recovery days alike. Under 30 seconds was already "Hung up before voicemail"; 45+ seconds with no outcome is still a conversation. Gino should log **"No Answer – Left Voicemail"** on these calls. (Claude's recommendation, pending Sheila.) |
| 10 | Stephen Wright: recovery Day 2 not called. Gino: he dialed fresh recoveries before follow-ups, so his follow-up smart view mixed them. | **Counts as a miss** (Gino admitted it; Jay confirmed). Gino now works follow-ups before fresh recoveries. |
| 11 | Fahim N: reschedule request not called; the lead asked to be reached after the holidays. | Excused (Jay). **When a lead asks to be contacted later, Gino creates a Close task on the lead for that date.** An open task already pauses the recovery sequence until its date (Nov 24 rule). Without the task it still shows as a miss for Sheila and Jay to decide. (Claude's recommendation, pending Sheila.) |


**From Jay's review of Gino's Nov 24 scorecard** ([thread](https://dylanhelen.slack.com/archives/C0CG28G7TQT/p1795606929345119)). Jay: "1–8 Confirmed … All good. Thanks!" Sheila left it to Jay and asked to hear about anything that keeps alerting when it shouldn't.

| # | What happened (Nov 24) | Decision / rule from now on |
|---|---|---|
| 1–6 | Peter Mosesian, Monica Y, Tim Canaley, Mike Lariza: the prospect was talking with the closer (texted Harry, asked Harry or Owen to resend the invite) and Gino marked them Confirmed without the day-before call or 5:45 cancel. | All excused (Jay). Gino said #2/#5 was a weak confirmation and he could have made the day-before call. That's hindsight next to a reason, not an admission, and Jay's "All good" excuses it. **Recurring pattern** (also Nov 23 #1–6 and Nov 25 #1, #3, #4): Jay excuses every "prospect is engaging with the closer, Gino marked Confirmed" item. Until Sheila decides otherwise, the rule stays: Gino logs **Closer Confirmed** in these cases, which removes the checks. |
| 7 | Ethan Menkin: logging. Moved to Confirmed with the invite not accepted; Ethan had only texted the closer "Yes I got it". | Excused (Jay). Same pattern as above. |
| 8 | Yehuda Schuster: "reschedule request speed: not called". The lead went to Reschedule Request – Recovery at 12:09pm ET Nov 24 and was corrected to No Show – Recovery at 2:11pm ET (the closer's EOD already said no-show). Gino started recovery the next day. | Excused (Jay). **When the recovery status is corrected before his first call, the corrected type applies.** A no-show has no 15-minute target, so no speed item. |

**Supabase check (Nov 27).** All 30 of Jay's decisions recorded so far match his replies. Two older items were recorded "unclear" although this log has them excused (Nov 16 #1 Dean B; Nov 17 #2 Inderjeet Harika, Sheila in a session). The morning run now takes decisions made in a session from this log when Slack alone is unclear (RUNBOOK step 4b).
---

## 00000000. Update Nov 24, 2026 (rev 10): call recovery tracking and pay

From Sheila, in the recovery design session (Nov 23–24). Full proposal and mockups: [`proposals/call-recovery/`](../proposals/call-recovery/README.md). This section replaces sections 2 (gate on the recovery bonus) and 7 (recovery) where they differ, and closes open items 1 and 2 (section 12) and E (section 0.6).

| Topic | Rule |
|---|---|
| **No gate on the recovery bonus** | Recovery is Gino's discretionary effort for the bonus. Nothing in recovery affects his base pay or base KPIs, and **the confirmation KPIs no longer gate the recovery bonus either**: every recovered call that shows pays $50. Sheila and Jay still approve the week on Tuesdays. Recovery steps are tracked and shown for coaching only. |
| **Counts from** | Recoveries from **Nov 24** (once the routine is turned on). |
| **Where recoveries book** | Every recovery (no-show, cancel, reschedule request) books on the **closers' round robin**, `sdrb_c2_startnow` (Calendly event "Discovery Call with SMB Deal Hunter Pro - O2C"). The setter calendar (`emorg_intro`) is no longer used for recovery. |
| **Credit** | All of: (1) Gino touched the lead after it entered recovery and before the rebook; (2) the new call is on the round robin; (3) **Calendly names Gino as the scheduler** (`invitee_scheduled_by` = his Calendly user `users/a657209b-e5aa-4e23-b2e8-d9699363b19b`): he books it himself while logged in and never sends the link; (4) nobody else tried to rebook the lead in between. Tested Nov 24: Sheila's own booking on the round robin recorded her as scheduler; public-link bookings record nobody. |
| **Pays** | $50 when the lead **shows** to that rebooked call ("showed" source order as section 9), once per original lost call. Max 2 rebooks per person; if the rebooked call no-shows, the same case reopens. Bonus week = the week the call shows. |
| **Lost calls (a row on the tracker)** | A lead lands in recovery: lead status `No Show - Recovery`, `Cancelled - Recovery` or `Reschedule Request - Recovery`. **His own 5:45 day-before cancels count.** Backlog leads get a row the first time he touches one. Lost calls found only by the Zoom backstop (the closer never moved them) are shown, flagged and **not scored**; he can label them and work them, and a rebook that shows still pays. |
| **5-day sequence** | Starts at **his first attempt**, not when the lead lands in recovery. Day 1: call, double dial, recovery voicemail, Day 1 text for the type. Day 2: double dial unless they pick up. Day 3: double dial, Day 3 voicemail and text. Day 4: double dial unless they pick up. Day 5: double dial, breakup voicemail and text, then stop. Ends early on a rebook or "Not Interested". A callback (an open Close task on the lead) pauses it until the task's date. If the closer is already rescheduling, Gino stays out; he takes over if the closer sent their own link and the lead hasn't replied in 24 hours. |
| **Reschedule requests** | One that comes in during his shift is tracked for a call within 15 minutes. One that comes in overnight has no speed target: it's due as Day 1 on his next shift. |
| **Logging** | The **Call Recovery** field each day (Day 1–5, Not Interested, Rebooked; Sheila renamed Day 3 and added Not Interested on Nov 24; no callback option). A **Call Confirmation Specialist** activity when he rebooks. |
| **Tracker** | New Recovery tab after Sheila's divider tab **"Call Recovery>>"** (renamed Nov 24). Daily/Weekly get recovery columns. Management's "Recovered calls that showed" is a **live formula** (Management → Daily → Recovery rows), never typed in. Recovery misses go on Reviews with a "Recovery" label; decisions are for coaching and never change the bonus. |
| **Scorecard** | Tue–Fri: a recovery row (steps: reschedule requests in 15 min, Day 1 full sequence, Days 2–5 on schedule, logging; results that day: rebooked by Gino, recovered calls that showed, bonus). The "X of 7 hit" pill counts confirmation only. On the **Monday card only** (Tue–Fri cards stay short), two funnels for last week (Sheila, Nov 24), with one bonus tile spanning both: **lost this week** (lost → worked → rebooked → showed → still ahead, and the bonus) and **older lost calls + backlog** (worked → rebooked → showed → still ahead). Still ahead = rebooked calls not held yet, part of rebooked. Showed counts the week the call is held, so all shows × $50 = the bonus. On the Recovery tab, a day after the lead was rebooked shows N/A; the day it was rebooked shows what Gino did and who booked it (Gino, or the lead through the public link). |

---

## 0000000. Update Nov 24, 2026 (rev 9): confirmed by phone or text is valid logging

From Sheila, Nov 24.

| Topic | Rule |
|---|---|
| **Confirmed by phone** | If the prospect verbally confirmed on the call (yes to the day and time, "I'll be there") and Gino logged them accepted (field 1, 3 or 9, or status Confirmed) before the calendar invite was accepted, that's **not a logging error**. No technical problem is needed. Gino usually also logs the outcome "Confirmed not Accepted" or field 5 and leaves a note. Those point to the call, but **the call transcript is the proof**: the morning run reads it and records "Valid (confirmed by phone)". No connected call, no transcript, or no clear confirmation ("I'll check my email") is still a logging error for Sheila and Jay. |
| **Confirmed by text** | Unchanged and confirmed: when the prospect texts that they'll attend, Gino logs them accepted, as he's been told. That's valid ("Valid (confirmed by text)", since Nov 18). |
| **Pre-check** | It doesn't read transcripts or new texts, so these can still appear there. It tells Gino there's nothing to do when he spoke to them or they texted; the morning run decides. |

---

## 000000. Update Nov 20, 2026 (rev 8): work after his shift counts; afternoon pre-check

From Sheila, Nov 20.

| Topic | Rule |
|---|---|
| **Work after 6pm MT** | Anything Gino does after his shift still counts. Every checkpoint looks to **midnight MT** of its day: welcome and follow-up calls (already), and now day-before calls, prospects confirming by phone, and the 5:45 cancel (a cancel after 6pm MT on the day before counts as done). Until Nov 20 the day-before call stopped at 6pm MT. The 5:45 cancel is still due at 5:45: a call after it doesn't excuse a missed cancel unless the prospect accepts or confirms by phone. |
| **Afternoon pre-check** | Weekdays by 5:30pm MT, a post in #cc-gino tags Gino with what would show as a miss on the next scorecard if nothing changes, and the 5:45 cancels coming up (`precheck/ROUTINE.md`). It's information only: no deadline, and it decides nothing. The morning run still decides. From Nov 23 the channel post is one sentence (day, activity time, counts) and the list goes in a thread reply under it, so it doesn't fill the channel. |

---

## 00000. Update Nov 19, 2026 (rev 7): SOP update for follow-ups and next-day bookings

From Sheila's SOP update (written Nov 18; Gino told the night of Nov 18). Decided with Claude on Nov 19.

| Topic | Rule |
|---|---|
| **Daily follow-up calls** | A call booked 2+ days out (booked before the day before) whose invite isn't accepted gets a call **every weekday** after the welcome call, until they accept or it's the day before. Double dial, then a voicemail if there's no answer. **No text.** Not due once they accept, confirm by text, or the closer or a setter confirmed, or if the call was cancelled. Scored from **Nov 19** (nothing earlier). **Counts toward KPI 1** like the other checkpoints. Gino works these from the Close smart view "Call Confirmation - Follow-up" (https://app.close.com/leads/save_urBC1kUukukmvDC15hu7tv6qOaZZKusQLLCZYlZa8by/, created by Sheila Nov 19). |
| **Texts for bookings made 2+ days out** | Only on the day before: double dial, voicemail, then the day-before confirmation text, then the 5:45 cancel if they still haven't accepted. Example: booked Wed for Sat. Wed welcome call and Thu follow-up with no text; Fri day-before call and text; not accepted by 5:45 Fri → cancel and send the day-before cancel text. |
| **Booked the evening before the day before** (e.g. Tue 10pm for a Thu call) | Booked 2+ days out. His first call is on the day before, so it's also the day-before call: it needs the day-before text, and the 5:45 cancel still applies. The smart view shows it as an overnight booking, so Gino may treat it like one; the tracker still expects the text (from Nov 19). |
| **Next-day bookings** (booked today for tomorrow) | The welcome call is also the day-before call: double dial, then the next-day voicemail. **No text** (the closer is texting them). **Never cancelled**, even if not accepted by 5:45. If Gino cancels one anyway, the tracker's 5:45 Result says so (not a miss). |
| **Monday calls** | No weekend shift, so no day-before call or 5:45 cancel. Follow-ups run through Friday (no text, no cancel). Anything left for the weekend isn't a miss. |
| **Hung up before the voicemail** | Still double dial. On a day-before call, still send the text. |
| **Welcome call script** | The "I'm your point of contact if you need to reschedule or cancel" line is removed (Gino doesn't text the lead). |
| **Call Confirmation outcome 2** | The Close option keeps its old name ("Welcome call – no answer: voicemail and text sent") so leads already logged with it keep their value. For welcome calls it now means voicemail left; no text is needed. |
| **Confirmed** | The invite is accepted, or the prospect texts that they'll be on the call (already the Nov 13 rule). |
| **Recovery booking** | Reschedule requests: book with the closers (round robin, `sdrb_c2_startnow`). No-shows and cancels: book on the setter calendar. If the closer already spoke with the lead, don't book; the closer recovers them. |

---

## 0000. Update Nov 18, 2026 (rev 6): Nov 17 scorecard review

**How reviews get decided from now on (Sheila, Nov 18):** Sheila and Jay decide every scorecard item in its #cc-gino thread (by end of the workday, after Gino explains around noon ET), "excused" or "still a miss", by number. The next morning's tracker run reads the thread and fills the Reviews tab (H-J) for them, including "Counts as a miss". They no longer edit the Reviews tab by hand; they open the tracker only to approve the week on the Management tab, **on Tuesdays** (Friday's card posts Monday and is decided that day, so the week is complete after Tuesday's morning run). They aim for a reply convention (`3, 5 excused - reason` / `7 miss`), but the run also reads free text. If they ever seem to disagree, the run reads the whole thread for the final word.

**From Sheila's review of Gino's Nov 17 scorecard** ([thread](https://dylanhelen.slack.com/archives/C0CG28G7TQT/p1795002144893109)):

| # | What happened (Nov 17) | Decision / rule from now on |
|---|---|---|
| 3, 5, 6 | Jessamyn Wilkinson, Michael Nunez, Neal Gustafson: welcome call missing only the text. | Excused. **The no-text rule for welcome calls applies from Nov 17**, not Nov 18. |
| 2 | Inderjeet Harika: both dials logged busy, 0 seconds; Gino's call note says "straight disconnect, didn't even ring", so no voicemail was possible. | Excused (Sheila, in a session). **A dial that never rang (busy/blocked/failed, 0 seconds) excuses the voicemail step.** **Before anything becomes a miss, read Gino's call and lead notes and check them against the Close activity**; a note the activity backs up excuses the step, otherwise the note goes on the Reviews row. |
| 4 | M Dwivedi was DQ'd from outbound and booked a D2C call themselves right away. | Excused (edge case). |
| 1 | Atembeoh Anu confirmed by phone, then rescheduled with Harry; the new booking was never called. | Miss stands. **After a reschedule, treat it as a new booking and call again.** (Already how the tracker counts it.) |
| 7, 8 | Lonnie Lockwood: no day-before call and no 5:45 cancel. | Misses stand (Gino agreed). |
| 9, 10, 11 | Elias Uddin texted "accept"; Franklin Steven texted "I will be there"; Jigya Dhamija tried to accept several times and Calendly errored. | Not logging errors. **A prospect's text saying they'll attend makes logging it accepted valid.** Before calling a logging error, read the texts between Gino and the prospect and his notes on the lead, not just the transcript. |

---

## 000. Update Nov 18, 2026 (rev 5): Nov 16 scorecard review and the sales leadership call

**From Sheila's review of Gino's Nov 16 scorecard** ([thread](https://dylanhelen.slack.com/archives/C0CG28G7TQT/p1794915785391219)):

| # | What happened (Nov 16) | Rule from now on |
|---|---|---|
| 2 | Edgar Parrado declined the invite on Sunday, before Monday's shift. Gino logged 8 and didn't dial. | **Cancelled before he reached them = no welcome call needed**, if the prospect cancelled the call or declined the invite before his first dial and he logged Call Confirmation 8. |
| 3 | Richard Davidson booked at 7:53pm ET. Gino dialed and confirmed him at 8:01pm ET, just after his shift. The tracker stopped looking at shift end. | **Look at the whole day, not just his shift.** New bookings are only due during his shift, but he keeps working, so a call made later the same day counts (to midnight MT). |
| 4, 5 | Atembeoh Anu and Stephen Wright confirmed by phone on the day before. Gino didn't cancel and wrote a note in Close. | Already the Nov 16 rule (spoke and confirmed by phone on the day before = no 5:45 cancel). The tracker clears them; only the old Reviews rows needed excusing. |
| 1 | Dean B (call Mon 12pm ET) dropped out of his smart view at 12pm, before Gino reached him (see below). | Excused: a smart view issue. Sheila added a meeting-time column to "Call Confirmation - New Booking" so he can sort and work the soonest calls first. |

**From the sales leadership call (Nov 18):**
- **Welcome calls: no text.** For new bookings and overnight bookings, a no-answer needs double dial + voicemail only. Day-before calls still need double dial + voicemail + text. The tracker applies this to welcome calls due from Nov 18 (moved to Nov 17 in rev 6).
- **No 5:45 cancel for next-day bookings.** The closer's slot can't realistically be refilled that late, and a short booking window goes with higher show rates. Calls booked 2+ days out that still aren't accepted at 5:45pm MT the day before are still cancelled. Nothing wider (Sheila, Nov 18: not "within 48 hours"). In the tracker this is the same as the Nov 13 rule "never cancel a booking made that same day": a call booked for the next day is booked on the day before.
- **Outreach to next-day bookings:** drop "Our system will cancel if not accepted". Ask them to accept the invite and to be on a laptop for Zoom. Calls booked 2+ days out keep the cancel language, because they can still be cancelled.

**Dean B (Nov 16), what happened:** Gino started dialing at 10:57am ET. Dean was booked Saturday 9:57pm ET for Monday 12pm ET and sat in "Call Confirmation - New Booking" at shift start (status Needs Confirmation, field blank). That view sorts by the newest status change first, so Saturday's bookings were at the bottom of a weekend's worth of new bookings. Gino worked newest to oldest and reached Saturday's bookings at about 12:13pm ET. At 12:00pm ET Dean's status moved to "Call in Progress", which took him out of the view before Gino got there. So he didn't start late; the view's sort order put the soonest call last. Fixed Nov 18: the view has a meeting-time column, and he works soonest first.

---

## 00. Update Nov 16, 2026 (rev 4): scoring rules from the Nov 13 scorecard thread

Gino explained all 8 items on his Fri Nov 13 scorecard in #cc-gino ([thread](https://dylanhelen.slack.com/archives/C0CG28G7TQT/p1794829426885189)). Sheila (Nov 16): every explanation makes sense, keep doing what he did, all eight are compliant, and the tracking rules should change to match. The tracker (`tracker/pipeline/build.py`), the scorecard and the Definitions tab now follow these rules:

| # | What happened (Nov 13) | Rule from now on |
|---|---|---|
| 1, 2, 4, 6 | The prospect picked up and hung up, or the call dropped, before he could leave a voicemail. He sent the texts. | **Hung up or dropped before voicemail = a step he couldn't do**, like "No VM option". The double dial and the text are still required. The tracker reads it from Close: an answered dial with no voicemail, under 30 seconds or logged "No answer / hung up". |
| 4, 6 | He left a voicemail earlier, then made one last call right before the 5:45 cancel without a second voicemail. | **One voicemail per checkpoint is enough.** The last call before the cancel needs no voicemail. The cancel text follows it. |
| 3 | The prospect called him back right after he dialed and confirmed on the phone. | **His calls right before the 5:45 cancel, and a prospect calling him back, count toward the day-before call.** The day-before window now runs to the end of his shift (6pm MT), not 5:45. |
| 5 | Booked overnight for the next day, so the welcome call and the day-before call were the same calls and showed up twice. | **One shift, one checkpoint.** When the welcome call falls on the day-before shift, it covers the day-before call. |
| 7 | He reached the prospect on the day before, who said they had accepted (it didn't show in Close). He noted it in Close and didn't cancel. | **Spoke and confirmed by phone on the day before = no 5:45 cancel.** He logs the outcome "Conversation: Confirmed not Accepted" and a note. The 5:45 cancel is for prospects he couldn't reach. |
| 8 | He cancelled at 5:45 as the process says; Calendly recorded the prospect as the canceller. | **Any cancel on the day before counts as the 5:45 cancel**, whoever Calendly names. Cancelling through the prospect's link records the prospect's name. |

- The Management tab caps "Misses you excused" at "Missed", so a Reviews row excused by hand that the new rules also clear isn't counted twice.
- Reviews rows already on the sheet are never rewritten. The eight Nov 13 rows still need "Excused" in column H (Sheila is doing this).
- "Confirmed = invite accepted" still holds for everything else. A spoken confirmation on the day before only removes the 5:45 cancel. It isn't an accepted invite, so he logs it as 5 (Spoke – not accepted yet), not 1, 3 or 9.

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
- **Steps he can't do aren't misses:** no voicemail option, a full mailbox, a text that won't send, a call hung up or dropped before the voicemail (rev 4).
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
