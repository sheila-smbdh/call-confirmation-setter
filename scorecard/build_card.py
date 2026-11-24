"""Offline: build Gino's daily scorecard data from the files plan.py told you to fetch. No network.

Usage: python3 -I scorecard/build_card.py DIR
Reads DIR/plan.json, runs.json, daily.json, reviews.json, dials.json, and (Nov 24) rec_days.json and rec_weeks.json
for the call recovery row and funnels (optional: the card still builds without them). Writes DIR/card.json (for render.js) and
DIR/message.txt (the Slack comment). Prints OK, or STALE / NO DATA with the reason (then send no card).

How each tile is counted (the same rules as the tracker's Reviews tab, docs/DECISIONS.md, newest sections first):
- A miss is a Reviews row for that day. Rows Sheila or Jay marked "Excused" don't count and leave the total too.
- Overnight: overnight bookings he had to call, minus the ones never dialed.
- Speed to lead: share of during-shift bookings first dialed within 15 min, out of all that were due (the same as
  KPI 2 on the Management tab; a booking never dialed counts as not in 15 min). Green at 85% or more, red below
  (Sheila, Nov 17). A booking never dialed is still listed under "Reply with why"; it is a KPI 1 miss.
- No-answer steps (was "VM + text" until Nov 19): no-answers where he did every step the call needs. Day-before calls:
  double dial + voicemail + text. Welcome calls (from Nov 17) and daily follow-up calls: double dial + voicemail, no
  text. build.py decides which steps each call needs.
- Day-before: day-before calls due, minus the ones not made.
- Follow-ups (from Nov 19): daily follow-up calls due (bookings 2+ days out, invite still not accepted, on the weekdays
  between the welcome call and the day before), minus the ones not made. Their no-answers count in No-answer steps, where
  double dial + voicemail is enough (no text).
- 5:45 cancels: unaccepted next-day calls that needed the cancel, minus the ones not cancelled.
- Logging: logging errors still open.
The "Reply with why" list is every open (not excused) Reviews row for that day.

What isn't a miss comes from tracker/pipeline/build.py, so the card follows it. Since Sheila's Nov 16 reply to the
Nov 13 card: a dial hung up or dropped before a voicemail could be left excuses the voicemail (No-answer steps tile); his
last calls before the 5:45 cancel and a prospect calling him back count toward the day-before call; a welcome call on
the day-before shift covers the day-before call (one item, not two); a prospect who confirmed by phone on the day
before needs no 5:45 cancel; and any cancel on the day before counts as the 5:45 cancel, whoever Calendly names.
"""
import json, re, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

D = sys.argv[1]
MT = ZoneInfo("America/Denver")
ld = lambda f: json.load(open(f"{D}/{f}"))
plan, runs, daily, reviews, dials = ld("plan.json"), ld("runs.json"), ld("daily.json"), ld("reviews.json"), ld("dials.json")
day = date.fromisoformat(plan["day"])
weekend = [date.fromisoformat(x) for x in plan["weekend"]]
rows = {r["day"]: r["row"] for r in daily}

through = date.fromisoformat(runs[0]["data_through"]) if runs and runs[0].get("data_through") else None
if not through or through < day or plan["day"] not in rows:
    print(f"STALE: the tracker has data through {through}, but the card needs {day}. Send no card.")
    sys.exit(1)

r = rows[plan["day"]]
g = lambda k: r.get(k) or 0
REC_KINDS = ("Recovery miss", "Recovery logging")
rec_reviews = [x for x in reviews if x.get("kind") in REC_KINDS]
reviews = [x for x in reviews if x.get("kind") not in REC_KINDS]
open_ = [x for x in reviews if (x.get("decision") or "").strip().lower() != "excused"]
excused = [x for x in reviews if (x.get("decision") or "").strip().lower() == "excused"]
cp = lambda xs, name: [x for x in xs if x["checkpoint"] == name]
untouched = lambda xs: [x for x in xs if x["what_happened"].startswith("Not touched")]
missing = lambda xs: [x for x in xs if x["what_happened"].startswith("Missing")]
WO, WS, DB, C545, LOG = "Welcome call (overnight)", "Welcome call (during shift)", "Day-before call", "5:45 cancel", "Logging"
FUP = "Follow-up call"


def frac(due, excused_n, missed_n):
    tot = max(int(due) - excused_n, 0)
    done = max(tot - missed_n, 0)
    return f"{done}/{tot}", ("g" if missed_n == 0 else "r")


ov_v, ov_s = frac(g("Welcome: overnight bookings / Due"), len(untouched(cp(excused, WO))), len(untouched(cp(open_, WO))))
ds_due = int(g("Welcome: during-shift bookings / Due"))
on_time = r.get("Welcome: during-shift bookings / On time %")
if ds_due and on_time is not None:
    # Daily's "On time %" is out of the bookings he dialed; the card (like KPI 2) is out of all that were due.
    in15 = round(on_time * g("Welcome: during-shift bookings / Touched"))
    sp_v = f"{round(in15 / ds_due * 100)}%"
    sp_t = f"{in15} of {ds_due} in 15 min"
    sp_s = "g" if in15 / ds_due >= 0.85 else "r"
else:
    sp_v, sp_t, sp_s = "–", "none booked", "g"
na = sum(g(f"{k} / No answer") for k in ("Welcome: overnight bookings", "Welcome: during-shift bookings", "Day-before calls",
                                         "Daily follow-up calls"))
st_v, st_s = frac(na, len(missing(excused)), len(missing(open_)))
db_v, db_s = frac(g("Day-before calls / Due"), len(untouched(cp(excused, DB))), len(untouched(cp(open_, DB))))
fu_v, fu_s = frac(g("Daily follow-up calls / Due"), len(untouched(cp(excused, FUP))), len(untouched(cp(open_, FUP))))
c_v, c_s = frac(g("5:45 resolutions / Needed a cancel"), len(cp(excused, C545)), len(cp(open_, C545)))
lg = len(cp(open_, LOG))

tiles = [
    ["Overnight", ov_v, "all dialed", ov_s],
    ["Speed to lead", sp_v, sp_t, sp_s],
    ["No-answer steps", st_v, "all done", st_s],
    ["Follow-ups", fu_v, "called", fu_s],
    ["Day-before", db_v, "called", db_s],
    ["5:45 cancels", c_v, "done", c_s],
    ["Logging", str(lg), "error" if lg == 1 else "errors", "g" if lg == 0 else "r"],
]


# ---- Nov 24: call recovery (information only; never affects pay or the "hit" pill) ----
import os
opt = lambda f: json.load(open(f"{D}/{f}")) if os.path.exists(f"{D}/{f}") else []
rdays = {x["payload"]["date"]: x["payload"] for x in opt("rec_days.json")}
rweek = (opt("rec_weeks.json") or [{}])[0].get("payload")
rec_open = [x for x in rec_reviews if (x.get("decision") or "").strip().lower() != "excused"]
rd = rdays.get(plan["day"], {})
def rfrac(due, ok):
    return (f"{ok}/{due}" if due else "–"), ("g" if ok == due else "r")
rr_v, rr_s = rfrac(rd.get("rr_due", 0), rd.get("rr_ok", 0))
d1_v, d1_s = rfrac(rd.get("d1_due", 0), rd.get("d1_ok", 0))
d25_v, d25_s = rfrac(rd.get("d25_due", 0), rd.get("d25_ok", 0))
le = rd.get("log_err", 0)
rec = None
if rdays or rweek:
    rec = {"effort": [["Resched. asks", rr_v, "called in 15 min", rr_s], ["Day 1 touch", d1_v, "full sequence", d1_s],
                      ["Days 2–5", d25_v, "on schedule", d25_s], ["Logging", str(le), "error" if le == 1 else "errors", "g" if le == 0 else "r"]],
           "result": [["Rebooked", str(rd.get("rebooked", 0)), "by you in Calendly", "i"],
                      ["Showed", str(rd.get("shows", 0)), "rebooked earlier", "i"],
                      ["Bonus", f"${rd.get('bonus', 0)}", "from those shows", "i"]]}
    if rweek:
        n, o = rweek["new"], rweek["older"]
        # two funnels (Sheila, Nov 24). Showed counts the week the new call is held, so showed x $50 = the bonus.
        # Still ahead = rebooked calls not held yet; they are part of rebooked.
        rows_ = [["Lost this week" if not weekend else "Lost last week",
                  [[str(n["lost"]), "lost calls"], [str(n["worked"]), "you worked"], [str(n["rebooked"]), "rebooked"],
                   [str(n["showed"]), "showed"], [str(n["ahead"]), "still ahead"], [f"${rweek['bonus']}", "bonus (all)", "pay"]]],
                 ["Older lost calls + backlog",
                  [["", "", "blank"], [str(o["worked"]), "you worked"], [str(o["rebooked"]), "rebooked"],
                   [str(o["showed"]), "showed"], [str(o["ahead"]), "still ahead"], ["", "", "blank"]]]]
        rec["funnels"] = {"title": ("This week's call recovery so far" if not weekend else "Last week's call recovery"),
                          "range": f"{date.fromisoformat(rweek['week']).strftime('%a %b')} {date.fromisoformat(rweek['week']).day} – "
                                   f"{(date.fromisoformat(rweek['week']) + timedelta(days=6)).strftime('%a %b')} {(date.fromisoformat(rweek['week']) + timedelta(days=6)).day}",
                          "rows": rows_}

def when(text):
    """'(call 11-13 1:00 PM)' or '(booked ..., call 11-13 1:00 PM)' -> 'call Fri 1:00pm ET'."""
    m = re.search(r"call (\d\d)-(\d\d) (\d+:\d\d) ([AP]M)", text)
    if not m:
        return ""
    dd = date(day.year + (1 if int(m[1]) < day.month else 0), int(m[1]), int(m[2]))
    return f"call {dd.strftime('%a')} {m[3]}{m[4].lower()} ET"


def what(x):
    t, c = x["what_happened"], x["checkpoint"]
    w = when(t)
    tail = f" ({w})" if w else ""
    if c == LOG:
        return t
    if t.startswith("Not touched"):
        return ("call not made" if c in (DB, FUP) else "never dialed") + tail
    if t.startswith("Missing"):
        steps = re.match(r"Missing ([^(]+)", t)[1].strip()
        return f"no-answer, missing {steps}" + tail
    if c == C545:
        if t.startswith("Cancelled on the day"):
            return "cancelled on the day of the call, not the day before" + tail
        return "not accepted and not cancelled" + tail
    return re.sub(r"\s*\(.*\)$", "", t) + tail


SEC = {WO: "Overnight", WS: "New booking", FUP: "Follow-up", DB: "Day-before", C545: "5:45 cancel", LOG: "Logging"}
ORDER = [WO, WS, FUP, DB, C545, LOG]
open_.sort(key=lambda x: (ORDER.index(x["checkpoint"]) if x["checkpoint"] in ORDER else 9, x["lead_name"].lower()))
name = lambda s: " ".join(w.capitalize() if w.isupper() else w for w in s.split())
ask = [[name(x["lead_name"]), SEC.get(x["checkpoint"], x["checkpoint"]), what(x)] for x in open_]
# recovery items come after the confirmation items; their label already says "Recovery ..."
ask += [[name(x["lead_name"]), x["checkpoint"], x["what_happened"]] for x in sorted(rec_open, key=lambda x: (x["checkpoint"], x["lead_name"].lower()))]

# Header: bookings to confirm, dials and first/last dial (MT) on the scored day.
ts = [datetime.fromisoformat(x["occurred_at"]).astimezone(MT) for x in dials]
et_day = lambda t: t.astimezone(ZoneInfo("America/New_York")).date()
day_ts = [t for t in ts if et_day(t) == day]
book = int(g("Welcome: overnight bookings / Due") + g("Welcome: during-shift bookings / Due")
           + g("Welcome: not counted / Accepted at booking (no call needed)"))
hm = lambda t: t.strftime("%-I:%M%p").lower()
stats = f"{book} bookings · {len(day_ts)} dials" + (f" · {hm(day_ts[0])}–{hm(day_ts[-1])} MT" if day_ts else "")
if day.weekday() == 4:
    stats += " · day-before and 5:45 = Saturday calls only"

wk = None
if weekend:
    parts = []
    for w in weekend:
        wr = rows.get(w.isoformat())
        n = sum(1 for t in ts if et_day(t) == w)
        lab = w.strftime("%a")
        if wr is None:
            parts.append(f"{lab} not in the tracker yet")
            continue
        due = sum((wr.get(f"Welcome: {k} bookings / Due") or 0) for k in ("overnight", "during-shift"))
        hit = sum((wr.get(f"Welcome: {k} bookings / Touched") or 0) for k in ("overnight", "during-shift"))
        parts.append(f"{lab} no calls" if not n else f"{lab} {hit} of {due} new bookings called, {n} dials")
    wk = "<b>Weekend (not scored):</b> " + " · ".join(parts)

fmt = lambda x: x.strftime("%a, %b ") + str(x.day)
today = date.fromisoformat(plan["today"])
card = {"day": fmt(day), "sent": f"Sent {fmt(today)}", "stats": stats, "tiles": tiles, "ask": ask, "weekend": wk, "rec": rec}
json.dump(card, open(f"{D}/card.json", "w"), indent=1)

hit = sum(t[3] == "g" for t in tiles)
msg = f"<@U0CFPJZQHGQ> your scorecard for {day.strftime('%A, %b ')}{day.day}: {hit} of {len(tiles)} call confirmation targets hit."
if rec and rd:
    msg += f" Call recovery: {rd.get('rebooked', 0)} rebooked, {rd.get('shows', 0)} showed (${rd.get('bonus', 0)})."
msg += (f" {len(ask)} item{'s' if len(ask) != 1 else ''} to explain: reply in this thread by noon MT, one line per number."
        if ask else " Nothing to explain. Nice work.")
# The numbered list goes in the post as text too, so the morning tracker run can match Sheila's and Jay's replies
# ("3, 5, 6 excused - reason" / "7 miss") to the right Reviews rows (Nov 18).
if ask:
    msg += "\n" + "\n".join(f"{i}. {a[0]} · {a[1]} · {a[2]}" for i, a in enumerate(ask, 1))
    msg += ("\n_Sheila / Jay: reply by number, e.g. `3, 5 excused - reason` or `7 miss`. "
            "The next morning's tracker run fills the Reviews tab from your replies._")
open(f"{D}/message.txt", "w").write(msg)
print("OK", json.dumps({"day": plan["day"], "hit": hit, "to_explain": len(ask), "dials": len(day_ts)}))
