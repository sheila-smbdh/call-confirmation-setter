"""Offline: Gino's afternoon pre-check. Lists what would show as a miss on the next scorecard if nothing changes, and the
5:45 cancels coming up. Information only: work after his shift still counts (to midnight MT). No network.

Usage: python3 -I precheck/preview.py DIR TODAY      (TODAY = today's date in US Eastern, YYYY-MM-DD)
Reads DIR/calls_new.json (from `build.py DIR TODAY preview`) and DIR/review_keys_prev.json (the Reviews keys already
in Supabase, `[{"review_key": ...}]`). Writes DIR/message.txt (the Slack post) and prints OK with the counts.

Which items: exactly what tracker/pipeline/reviews.py would turn into Reviews rows (the scorecard's "Reply with why"
list), using its own items() function, for today's checkpoints, plus any logging error not already on the Reviews tab.
- 5:45 cancels that aren't due yet go in their own "coming up" list: they aren't misses until 5:45pm MT.
- Speed to lead can't be fixed after the fact; it's one line of information.
- The pre-check doesn't read Gino's lead notes or new prospect texts (the morning run does, runbook steps 7b and 7c), so
  an item a note or a text explains can still appear here. The post tells him to leave a note in that case.
"""
import json, os, re, sys
from datetime import date, datetime, timedelta, time
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tracker", "pipeline"))
from reviews import items  # noqa: E402  (same miss rules as the morning run)

D, TODAY = sys.argv[1], date.fromisoformat(sys.argv[2])
ET, MT = ZoneInfo("America/New_York"), ZoneInfo("America/Denver")
rows = json.load(open(f"{D}/calls_new.json"))
have = {x["review_key"] for x in json.load(open(f"{D}/review_keys_prev.json"))}

# "As of": when Gino's calls were pulled (the newest activity file), not when this script runs.
acts = [f"{D}/{f}" for f in os.listdir(D) if f.startswith(("g_call_", "g_sms_", "g_ev_"))]
asof = datetime.fromtimestamp(min(os.path.getmtime(f) for f in acts), ZoneInfo("UTC")).astimezone(MT) if acts \
    else datetime.now(MT)
cutoff = datetime.combine(TODAY, time(19, 45), ET)          # 5:45pm MT
next_card = TODAY + timedelta(days=3 if TODAY.weekday() == 4 else 1)

WO, WS, DB, C545, LOG, FUP = ("Welcome call (overnight)", "Welcome call (during shift)", "Day-before call",
                              "5:45 cancel", "Logging", "Follow-up call")
SEC = {WO: "Overnight", WS: "New booking", FUP: "Follow-up", DB: "Day-before", C545: "5:45 cancel", LOG: "Logging"}
ORDER = [WO, WS, FUP, DB, C545, LOG]


def when(text):
    """'(call 11-13 1:00 PM)' -> 'call Fri 1:00pm ET'."""
    m = re.search(r"call (\d\d)-(\d\d) (\d+:\d\d) ([AP]M)", text)
    if not m:
        return ""
    dd = date(TODAY.year + (1 if int(m[1]) < TODAY.month else 0), int(m[1]), int(m[2]))
    return f"call {dd.strftime('%a')} {m[3]}{m[4].lower()} ET"


def fix(cp, t):
    """What he can do now, in a few words."""
    if cp == LOG:
        return ("set Confirmed only once the invite is accepted; if they confirmed by phone or text, or couldn't accept, "
                "add a note on the lead saying so")
    if t.startswith("Not touched"):
        return "call now: double dial + voicemail + text" if cp == DB else "call now: double dial + voicemail"
    if t.startswith("Missing"):
        steps = re.match(r"Missing ([^(]+)", t)[1].strip()
        todo = {"double dial": "dial twice within 3 min", "voicemail": "leave a voicemail", "text": "send the text"}
        return "; ".join(todo.get(s.strip(), s.strip()) for s in steps.split(","))
    return ""


def what(cp, t):
    w = when(t)
    tail = f" ({w})" if w else ""
    if cp == LOG:
        later = re.search(r"\. (Prospect later declined.*)$", t)
        return "logged as accepted, but the calendar invite wasn't accepted" + (f" ({later[1].lower()})" if later else "")
    if t.startswith("Not touched"):
        return ("call not made" if cp in (DB, FUP) else "never dialed") + tail
    if t.startswith("Missing"):
        return "no-answer, missing " + re.match(r"Missing ([^(]+)", t)[1].strip() + tail
    return re.sub(r"\s*\(.*\)$", "", t) + tail


name = lambda s: " ".join(w.capitalize() if w.isupper() else w for w in s.split())
fixes, coming = [], []
for wk, d, cp, kind, lead, t, note, key in items(rows):
    if key in have:
        continue                                   # already on the Reviews tab
    if cp != LOG and d != TODAY:
        continue                                   # other days are already final (or not due yet)
    if cp == C545 and datetime.now(ET) < cutoff:
        if t.startswith("Not cancelled"):
            w = when(t)
            coming.append(f"{name(lead)}" + (f" ({w})" if w else ""))
        continue
    fixes.append((ORDER.index(cp) if cp in ORDER else 9, name(lead), SEC.get(cp, cp), what(cp, t), fix(cp, t)))
fixes.sort()

# Speed to lead today (KPI 2): during-shift bookings due today, first dialed within 15 min. Can't be fixed now.
ds = [r for r in rows if r.get("w_required") == "Yes" and r.get("booking_type") == "During shift" and r.get("w_due")
      and datetime.fromisoformat(r["w_due"]).astimezone(ET).date() == TODAY and r.get("w")]
in15 = sum(1 for r in ds if r["w"].get("on_time"))

day_s = lambda x: x.strftime("%a %b ") + str(x.day)
hm = lambda x: x.strftime("%-I:%M%p").lower()
msg = (f"<@U0CFPJZQHGQ> Pre-check for today, {day_s(TODAY)} (your Close activity as of {hm(asof)} MT). ")
if fixes:
    msg += (f"If nothing changes, {'this shows' if len(fixes) == 1 else f'these {len(fixes)} show'} as "
            f"{'a miss' if len(fixes) == 1 else 'misses'} on {next_card.strftime('%A')}'s scorecard:\n")
    msg += "\n".join(f"{i}. {n} · {s} · {w} → {f}" for i, (_, n, s, w, f) in enumerate(fixes, 1))
else:
    msg += f"Nothing would show as a miss on {next_card.strftime('%A')}'s scorecard so far. Keep it up."
if coming:
    msg += ("\n*5:45pm MT cancels coming up* (cancel unless they accept or confirm by phone before then):\n"
            + "\n".join(f"• {c}" for c in coming))
if ds:
    msg += f"\nSpeed to lead today: {in15} of {len(ds)} new bookings dialed within 15 min (already final)."
msg += ("\n_Couldn't do a step (didn't ring, number disconnected, no voicemail box)? Leave a note on the lead saying why. "
        "The morning run reads your notes before it marks a miss. Anything booked after this check is still due as usual._")
open(f"{D}/message.txt", "w").write(msg)
print("OK", json.dumps({"day": TODAY.isoformat(), "asof_mt": asof.strftime("%H:%M"), "to_fix": len(fixes),
                        "cancels_coming": len(coming), "speed": f"{in15}/{len(ds)}"}))
