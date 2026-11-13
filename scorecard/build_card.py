"""Offline: build Gino's daily scorecard data from the files plan.py told you to fetch. No network.

Usage: python3 -I scorecard/build_card.py DIR
Reads DIR/plan.json, runs.json, daily.json, reviews.json, dials.json. Writes DIR/card.json (for render.js) and
DIR/message.txt (the Slack comment). Prints OK, or STALE / NO DATA with the reason (then send no card).

How each tile is counted (the same rules as the tracker's Reviews tab, docs/DECISIONS.md section 0):
- A miss is a Reviews row for that day. Rows Sheila or Jay marked "Excused" don't count and leave the total too.
- Overnight: overnight bookings he had to call, minus the ones never dialed.
- Speed to lead: share of during-shift bookings first dialed within 15 min (target 85%). Red below 85%, or if a
  during-shift booking was never dialed.
- VM + text: no-answers where he did double dial + voicemail + text.
- Day-before: day-before calls due, minus the ones not made.
- 5:45 cancels: unaccepted next-day calls that needed the cancel, minus the ones not cancelled.
- Logging: logging errors still open.
The "Reply with why" list is every open (not excused) Reviews row for that day.
"""
import json, re, sys
from datetime import date, datetime
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
open_ = [x for x in reviews if (x.get("decision") or "").strip().lower() != "excused"]
excused = [x for x in reviews if (x.get("decision") or "").strip().lower() == "excused"]
cp = lambda xs, name: [x for x in xs if x["checkpoint"] == name]
untouched = lambda xs: [x for x in xs if x["what_happened"].startswith("Not touched")]
missing = lambda xs: [x for x in xs if x["what_happened"].startswith("Missing")]
WO, WS, DB, C545, LOG = "Welcome call (overnight)", "Welcome call (during shift)", "Day-before call", "5:45 cancel", "Logging"


def frac(due, excused_n, missed_n):
    tot = max(int(due) - excused_n, 0)
    done = max(tot - missed_n, 0)
    return f"{done}/{tot}", ("g" if missed_n == 0 else "r")


ov_v, ov_s = frac(g("Welcome: overnight bookings / Due"), len(untouched(cp(excused, WO))), len(untouched(cp(open_, WO))))
ds_due = int(g("Welcome: during-shift bookings / Due"))
on_time = r.get("Welcome: during-shift bookings / On time %")
sp_open = untouched(cp(open_, WS))
if ds_due and on_time is not None:
    sp_v = f"{round(on_time * 100)}%"
    sp_t = f"{round(on_time * ds_due)} of {ds_due} in 15 min"
    sp_s = "g" if on_time >= 0.85 and not sp_open else "r"
else:
    sp_v, sp_t, sp_s = "–", "none booked", "g"
na = sum(g(f"{k} / No answer") for k in ("Welcome: overnight bookings", "Welcome: during-shift bookings", "Day-before calls"))
st_v, st_s = frac(na, len(missing(excused)), len(missing(open_)))
db_v, db_s = frac(g("Day-before calls / Due"), len(untouched(cp(excused, DB))), len(untouched(cp(open_, DB))))
c_v, c_s = frac(g("5:45 resolutions / Needed a cancel"), len(cp(excused, C545)), len(cp(open_, C545)))
lg = len(cp(open_, LOG))

tiles = [
    ["Overnight", ov_v, "all dialed", ov_s],
    ["Speed to lead", sp_v, sp_t, sp_s],
    ["VM + text", st_v, "every no-answer", st_s],
    ["Day-before", db_v, "called", db_s],
    ["5:45 cancels", c_v, "done", c_s],
    ["Logging", str(lg), "error" if lg == 1 else "errors", "g" if lg == 0 else "r"],
]


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
        return ("call not made" if c == DB else "never dialed") + tail
    if t.startswith("Missing"):
        steps = re.match(r"Missing ([^(]+)", t)[1].strip()
        return f"no-answer, missing {steps}" + tail
    if c == C545:
        return "not accepted and not cancelled" + tail
    return re.sub(r"\s*\(.*\)$", "", t) + tail


SEC = {WO: "Overnight", WS: "New booking", DB: "Day-before", C545: "5:45 cancel", LOG: "Logging"}
ORDER = [WO, WS, DB, C545, LOG]
open_.sort(key=lambda x: (ORDER.index(x["checkpoint"]) if x["checkpoint"] in ORDER else 9, x["lead_name"].lower()))
name = lambda s: " ".join(w.capitalize() if w.isupper() else w for w in s.split())
ask = [[name(x["lead_name"]), SEC.get(x["checkpoint"], x["checkpoint"]), what(x)] for x in open_]

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
card = {"day": fmt(day), "sent": f"Sent {fmt(today)}", "stats": stats, "tiles": tiles, "ask": ask, "weekend": wk}
json.dump(card, open(f"{D}/card.json", "w"), indent=1)

hit = sum(t[3] == "g" for t in tiles)
msg = f"<@U0CFPJZQHGQ> your scorecard for {day.strftime('%A, %b ')}{day.day}: {hit} of {len(tiles)} targets hit."
msg += (f" {len(ask)} item{'s' if len(ask) != 1 else ''} to explain: reply in this thread by noon MT, one line per number."
        if ask else " Nothing to explain. Nice work.")
open(f"{D}/message.txt", "w").write(msg)
print("OK", json.dumps({"day": plan["day"], "hit": hit, "to_explain": len(ask), "dials": len(day_ts)}))
