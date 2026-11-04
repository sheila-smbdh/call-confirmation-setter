# Pre-call confirmation: findings

How closers and setters confirm 45-minute closer calls before they happen, and what that does to show rate. It feeds the setter-set confirmation proposal Sheila is taking to leadership.

- **Report:** https://claude.ai/artifact/WSFZVSxhYic1cKJ2JSfMgH (private). A copy is at `report.html`.
- **Scope:** the Call Confirmation Specialist confirms **direct-to-closer** calls only. **Setter-set** calls are confirmed by the setter and the closer, and the specialist doesn't touch them (see `docs/DECISIONS.md`).

Last updated: 2026-11-04.

---

## 1. Six months: May 1 – Oct 31, 2026

**Sample:**
- 5,307 closer calls.
- 3,752 have a show result: not cancelled, with a Zoom result. VeJohn is excluded because his meetings have no Zoom data.
- Built with `calls6.py` and `analyze6.py`.

### Headline numbers

| Measure | Result |
|---|---|
| Setter-set show rate | **78%** (866/1,109) |
| Direct show rate | **71%** (1,884/2,643) |
| Setter-set vs direct, within the same closer | **+7.5 pts** (95% CI +4.3 to +10.7). Holds within closer and month too (+6.9). |
| Show rate when the lead accepted the invite | **88%**, for setter-set and direct calls alike |
| Show rate when the invite wasn't accepted | 64% setter-set, 53% direct |
| Invite acceptance rate | 56% setter-set, 50% direct |
| Share of calls that are setter-set | 50% in May, down to 21–25% in Sep–Oct |

Setter-set calls showed more than direct calls in five of six months. May was about even. In October the gap was smallest: 75% vs 72% on Zoom. October's EOD-based 66% vs 68% came from a different method and a smaller sample.

### By setter (setter-set calls)

| Setter | Sets | Showed | Invite accepted | Texted day before* | Texted day of |
|---|---|---|---|---|---|
| Dave | 257 | 87% (174/201) | 62% | 74% | 4% |
| Yobani | 162 | 85% (108/127) | 62% | 69% | 9% |
| Jose | 111 | 81% (76/94) | 52% | 7% | 25% |
| Quinn | 228 | 77% (140/181) | 48% | 5% | 52% |
| Bali | 101 | 76% (64/84) | 49% | 18% | 14% |
| Gabriel | 237 | 74% (134/181) | 52% | 14% | 5% |
| Jordan K | 235 | 74% (136/185) | 66% | 28% | 9% |
| Omar (May–Jun, before closing) | 70 | 61% (34/56) | 44% | 0% | 0% |

\* On calls booked 2+ days ahead.

- Dave and Yobani's sets show **86%** (282/328), against **75%** (584/781) for the other setters: +11.4 pts within closer (95% CI +6.0 to +16.8).
- What sets them apart is texting the lead the day before on about 70% of their sets, and rarely on the day.

### Setter day-before text

| Comparison | Result |
|---|---|
| Overall | 81.7% (237/290) with the text vs 74.2% (449/605) without |
| Within the same closer | +8.2 pts (p = 0.008) |
| Within closer and month | +7.7 pts |
| Within closer and how far ahead the call was booked | +8.4 pts |
| **Within the same setter** | **+1.0 pts** (95% CI −6.2 to +8.2), not significant |

- The lift comes from the setters who make the text routine, so the habit can't be separated from the setter.
- It is the strongest pattern in the data, but not proof that the text causes the show.
- It goes with invite acceptance: when Dave texted the day before, 67% of his leads accepted, against 48% when he didn't.

### Day-of texts (setter-set calls)

| Who texted on the day | Showed |
|---|---|
| No one | 77.5% (565/729) |
| Setter only | 80.0% (120/150) |
| Closer only | 80.6% (170/211) |
| Setter **and** closer | **57.9%** (11/19) |

- **No lift from day-of texts.**
  - Setter day-of: −0.5 pts within closer.
  - Closer day-of: −3.2 pts.
  - Any day-of text: +0.6 pts.
- **Two senders on the same day is the worst pattern:** −22.9 pts against one sender, within closer (95% CI −42 to −4).
  - It's a small sample.
  - About half of those texts were replies to leads who had already written, so some of those leads were already wobbling.
- **Your three-text workflow** (setter day-before, setter day-of, closer day-of) happened only twice in six months, so it can't be judged from past data.

### Direct calls

- Closer day-of texts: no lift (+0.8 pts within closer).
- Closer **proactive** day-before texts: −10 pts (p = 0.01). These most likely go to leads who already look shaky.
- The automated pre-call email the day before: +3.8 pts (p = 0.08).

---

## 2. October deep-dive: Oct 3 – Nov 2, 2026

Built with `analyze.py` and `split.py`. Show results come from the EOD Tracker. The detail is in the lower half of the report.

### Closer confirmation habits

| Closer | What they do |
|---|---|
| Adam L | Confirms **86%** of calls on the day, with one saved template about 2 hours before the call. |
| Nick | Writes day-before texts, but **33 of 34 were unsent drafts** in Close. |
| Solomon | Texts only at-risk calls (invite unaccepted or "maybe"). |
| Tyler, Julien, Oliver | Confirm a quarter to a third of calls. |
| Everyone else | Rarely. Nobody confirms by phone. |

- Day-before contact is almost all the automated "NEW Pre-Call Workflow" email sequence.

### Setter-set vs direct (EOD-based)

- 197 calls (23%) were setter-set and 678 were direct.
- Show rates were 66% vs 68% on the EOD Tracker.
- Over six months on Zoom, setter-set calls show more (section 1).

### What leads say before the call

From another session, merged into the report.

- 46% of calls had a message from the lead, and 31% had a back-and-forth with both sides writing.
- 24% had a reschedule or cancel signal. Those calls showed 41%, against 62% for calls where the lead never wrote.
- 28 of 93 reschedule or cancel requests were replies to the automated "[Pro] You're confirmed… one last thing" email. It goes out in the closer's name, so **closers keep watching that inbox** whoever does the confirming.
- Whoever confirms will get the replies: reschedules, "resend the invite", "can I bring my partner". Setters need a way to move the call and resend the invite.
- Price and program questions go to the closer.

---

## 3. Proposal for setter-set calls

### Agreed so far (Sheila's takeaways, checked against the data)

1. **The day-before text's job is to get the invite accepted.** Supported: an accepted invite is the strongest predictor of showing.
2. **The setter and the closer should not both text the lead on the day.** Supported as a rule. The data shows no benefit from two texts and the worst show rate, though the sample is too small to prove they cause no-shows.
3. **The setter confirms the day before.** This is the best-supported step. It's what the best-showing setters do, but within the same setter the lift is small, so the 4-week test has to confirm it.
4. **Setter day-of: one very short text.** For example: "Excited to hear how your call with [Closer] goes today at [Time]!"
   - It performs the same as a closer-only text (80.0% vs 80.6%), so either is supported.
   - The setter version keeps the warm handoff.
   - Add the Zoom link if the invite still isn't accepted that morning.
   - Expect a small effect: Quinn texts on the day of half her sets, and hers show at the team average.
5. **No confirmation text from the closer on setter-set calls.** Supported: closer day-of texts added nothing measurable. The closer still handles replies to the automated "You're confirmed" email.

### Open choice for leadership

There are two versions of the day-of text, and the data can't choose between them:

- **Setter only:** Sheila's latest view, takeaways 4 and 5 above.
- **Closer one-liner:** the version currently in the report.

Either way, there is **one day-of text from one person**.

### Templates

**Setter, day before** (Sheila's draft, with the agreed edits):

> Hey [First Name]! Just a reminder about your call tomorrow with [Closer Name] at [Time] [TZ]. [Closer Name] has already reviewed your application and my notes, and has a presentation ready for you. Please join from a laptop so you can see everything [Closer Name] shares, and accept the calendar invite if you haven't yet. Still good for [Time] [TZ]? If you can't find the invite, I'll resend it.

- Before using "our system may automatically cancel the call if it's not accepted", confirm it's true.
- Templates should say who is who. One lead thought they were booked with both the closer and the setter. For example: "I'm Jose, I set up your call; VeJohn is the advisor you'll meet."

**Setter, day of:**

> Hey [First Name]! Excited to hear how your call with [Closer Name] goes today at [Time]. Let me know if I can help with anything!

**Closer, day of** (only if leadership picks the closer version):

> Hey [Name], [Closer] here. Looking forward to talking at [Time]!

### How to measure it

- Save every text as a Close SMS template, so adoption shows up through `template_id`.
- Run it for 4 weeks.
- Compare against the six-month baseline, measured the same way, with Zoom attendance and cancelled calls left out:
  - **Setter-set show rate:** 78% (75% in October).
  - **Invite acceptance:** 56% (58% in October).

---

## 4. Method

- **Calls:** 45-minute Close meetings, one per lead and start time, including closers who have since left: EJ (Ezra Isla), Chris, Kameron, Giovana, Jordan W (Jordan Worth). "Jay Z" is Jordan Zadrozny.
- **Showed (six months):** the prospect joined the Zoom, meaning anyone other than Close staff or a notetaker bot (DECISIONS.md §10).
  - Checked against EOD lead results for Sep–Oct: Zoom agreed on 94% of EOD shows (582/616) and 99% of EOD no-shows (188/190).
  - A Zoom room that never opened counts as unknown, because EOD outcomes split across it.
  - The EOD Tracker only lists individual leads from **Sep 2026**. Before that it has daily totals only.
- **Cancelled meetings** (declined by the org or the lead, or cancelled) are left out of show rates. Close doesn't record when a cancel happened, so same-day cancels can't be counted as no-shows the way the tracker does. Six-month show rates therefore run higher than tracker show rates.
- **Setter-set:** a setter meeting with the lead, or a setter call of 2+ minutes, in the 21 days before the booking up to 2 hours after it.
  - The "Conversation: set to closer" outcome only exists from Oct 2026, so it isn't used for the six-month split.
  - Omar counts as a setter only for his 15-minute meetings before June.
- **Touches counted:** sent texts, outbound dials and non-sequence emails from the call's closer or a setter, after booking and before the call, on the ET calendar day before or the day of the call.
  - Excluded: anything within 1 hour of booking, booking welcome texts, bulk blasts, drafts and failed sends, and the last 10 minutes before the call.
  - **Proactive** means no inbound text or email from the lead in the 3 hours before.
- **Within-closer differences** are Mantel-Haenszel-style pooled differences across closers (or the strata named), with a normal-approximation 95% CI.
- **Not visible:** texts and calls from personal phones.

### Setters and their Close users

| Setter | Close user ID |
|---|---|
| Dave (David Martin, `david@`) | `user_sByZkVjk2If3ioL4CC26O5JmTWuzzKzDEjr9fzZHJ26` |
| Jordan K | `user_3IrYZLUcCBZrg2mb49wCybrxGBFTCxa5eqTHhE1ApuC` |
| Gabriel | `user_rtKYgVTxSrwnTd5wJJA5Y6jr4gteTRTV1BloPCzuWXQ` |
| Quinn | `user_fXLAvRIRIJxMAgcaYa2hH14SuwQphwF5aC9vtvouHob` |
| Yobani | `user_TH3XzqxRNb7WhZ5taaJ9v3df27VAaU6KvCnFlCUbq9v` |
| Bali | `user_c0wPSKtEPsqkIh08OnjiGaj6XHeFBjGSp2jyVxAggDl` |
| Jose | `user_msFtSHmZcoRAYvHX8aGrnygBzOy4u1GnLrRSFfIdcgk` |

The October handoff's Dave ID (David Rendon, `dave@`) was wrong.

### Re-running

1. **Pull the meetings** into `close/m6/` with inline read-only search calls (see the handoff README for the recipe):
   - `meet/`: 45-minute meetings, fields including `attendees` and `integrations`.
   - `setter/`: setter meetings and setter calls of 2+ minutes.
   - `users.json`: the Close user list.
2. **Build the batched queries:** `python3 -I prep_bodies.py` writes lead-batched search bodies into `close/m6/body/`.
3. **Run each body as one read-only search:**
   ```bash
   curl -s -u "$CLOSE_API_KEY:" -X POST "https://api.close.com/api/v1/data/search/" -H "Content-Type: application/json" -d @close/m6/body/NAME.json -o close/m6/touch/NAME.json
   ```
4. **Check each result:** `python3 -I prep_bodies.py check NAME`. It splits a full 200-row page automatically.
   - Close's count can be one higher than the rows it returns, so only a full page counts as cut off.
   - `python3 -I prep_bodies.py todo` lists what's left.
5. **Run the analysis:** `python3 -I analyze6.py`.
6. **Validate shows:** for the EOD check, `eod/eod_sepoct.txt` holds the Sep–Oct EOD lead lists.

Raw pulls, `eod/` and `rows6.json` contain lead data and are git-ignored.

## 5. Open items

| # | Item | Owner |
|---|---|---|
| 1 | Pick the day-of sender for setter-set calls: setter only or closer one-liner | Sheila → leadership |
| 2 | Confirm the "may auto-cancel if not accepted" claim before putting it in the template | Sheila |
| 3 | Rebuild the October closer sections of the report at six months (offered) | Claude, if wanted |
| 4 | "What leads say" at six months needs one more pull of lead messages from booking onward | Claude, if wanted |
| 5 | VeJohn's meetings have no Zoom data in Close; check whether his Zoom is connected | Sheila |
| 6 | Confirm Gabriel is still setting (no activity after August) | Sheila |
