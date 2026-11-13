# Offline: pick the calls this run rebuilds, from saved Calendly + Close files. No network.
# Usage: python3 -I scope.py DATA_DIR TODAY   (TODAY = ET run date, YYYY-MM-DD) -> DATA_DIR/scope.json
# In scope: direct discovery bookings (Calendly event type ...3de6762f19f4) booked in the last 3 days or with a call
# from 3 days ago to 4 days ahead.
import json, sys, glob
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
D = sys.argv[1]
ET = ZoneInfo("America/New_York")
p = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
users = {u["email"].lower(): u for u in json.load(open(f"{D}/users.json"))["data"] if u.get("email")}
E = [json.loads(l) for l in open(f"{D}/cal_events.jsonl")]
M = {}
for f in sorted(glob.glob(f"{D}/meet_*.json")):
    for m in json.load(open(f))["data"]:
        M[m["id"]] = m
from datetime import date as _d, timedelta as _td, time as _t
TODAY = _d.fromisoformat(sys.argv[2])
_et = lambda d: datetime.combine(d, _t(0, 0), ET)
W0, W1 = _et(TODAY - _td(days=3)), datetime.now(timezone.utc)      # bookings made in the last 3 days, up to this run
S0, S1 = _et(TODAY - _td(days=3)), _et(TODAY + _td(days=5))        # calls from 3 days ago to 4 days ahead
rows = []
for e in E:
    if not e["event_type"].endswith("3de6762f19f4"):
        continue
    c, s = p(e["created"]), p(e["start"])
    if not (W0 <= c < W1 or S0 <= s < S1):
        continue
    host = (e["hosts"] or [""])[0].lower()
    uid = users.get(host, {}).get("id")
    cands = [m for m in M.values() if m["user_id"] == uid and p(m["starts_at"]) == s]
    rows.append(dict(e, host=host, uid=uid, close=[(m["id"], m["lead_id"], m["status"], m["title"]) for m in cands]))
json.dump(rows, open(f"{D}/scope.json", "w"), indent=0)
print(len(rows), "in scope;", sum(1 for r in rows if not r["close"]), "unmatched;", sum(1 for r in rows if len({x[1] for x in r["close"]}) > 1), "ambiguous")
for r in rows:
    if len({x[1] for x in r["close"]}) != 1:
        print(r["status"], r["start"], r["created"], r["host"], r["close"])
# Calendly invitee details still needed for this run (time zone, email, rescheduled flag): one URI per line.
have = set()
try:
    for l in open(f"{D}/cal_invitees.jsonl"):
        have.add(json.loads(l)["event_uri"])
except FileNotFoundError:
    pass
need = [r["uri"] for r in rows if r["uri"] not in have]
open(f"{D}/need_invitees.txt", "w").write("\n".join(need) + ("\n" if need else ""))
print(len(need), "events need Calendly invitee details (see need_invitees.txt)")
