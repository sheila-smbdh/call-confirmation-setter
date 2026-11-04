"""Offline: split closer calls into setter-set vs direct-to-closer, with confirmation and show rates. No network."""
import json, glob, os, re
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
NOW = datetime(2026, 11, 3, 5, 0, tzinfo=timezone.utc)
SET_TO_CLOSER = "outcome_034XYnwGD1sz2iKRzZAeuk"
p = lambda ts: datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None

BOOKING_RE = re.compile(r"accept the calendar invite|Just reading through your app|you'll see a few emails come through|leading up to our call, you'll be receiving emails", re.I)
CALL_RE = re.compile(r"\b(call|zoom|today|tomorrow|tonight|meeting|confirm)\b", re.I)

def norm(t):
    t = re.sub(r"\b(Hey|Hi|Hello|Good morning|Morning)\s+\w+", r"\1 X", t or "")
    t = re.sub(r"\d{1,2}(:\d{2})?\s*(am|pm|AM|PM)?\s*(ET|EST|EDT|CT|PT|MT|CST|PST|MST)?", "#", t)
    return re.sub(r"\s+", " ", t).strip()[:90]

def load(dirname):
    out = defaultdict(lambda: defaultdict(list))
    for f in glob.glob(os.path.join(HERE, "close", dirname, "*.json")):
        b = os.path.basename(f)
        who, typ = b.split("_")[:2]
        d = json.load(open(f))
        out[who][typ].extend(d.get("data", []))
    return out

closers = load("raw")
setters = load("setter")
setter_names = [s for s in setters if s not in ("settocloser",)]

# ---- EOD outcomes
name2 = {"AdamL": "adam", "JulienB": "julien", "NickV": "nick", "HarryW": "harry", "DanielJ": "daniel", "KevinM": "kevin", "VeJohnC": "vejohn", "SolomonH": "solomon", "OmarK": "omar", "OwenH": "owen", "JordanZ": "jayz", "TylerJ": "tyler", "OliverE": "oliver"}
eod = {}
for line in open(os.path.join(HERE, "eod", "eod_oct.txt")):
    d, c, _, rest = line.rstrip("\n").split("|")
    if c not in name2:
        continue
    for part in filter(None, rest.split(";")):
        k, ids = part.split(":")
        for i in ids.split(","):
            eod[(name2[c], "2026-" + d, i)] = k

# ---- setter evidence per lead
setter_mtgs = defaultdict(list)   # lead -> [(start, setter)]
for s in setter_names:
    for m in setters[s]["meeting"]:
        if m.get("lead_id"):
            setter_mtgs[m["lead_id"]].append((p(m["starts_at"]), s))
set_calls = defaultdict(list)     # lead -> [time] ("Conversation: set to closer" by anyone)
for f in glob.glob(os.path.join(HERE, "close", "setter", "settocloser_*.json")):
    for c in json.load(open(f))["data"]:
        if c.get("lead_id"):
            set_calls[c["lead_id"]].append(p(c["date_created"]))
for s in setter_names:
    for c in setters[s]["call"]:
        if c.get("outcome_id") == SET_TO_CLOSER and c.get("lead_id"):
            set_calls[c["lead_id"]].append(p(c["date_created"]))

for s_ in setter_names:
    for c in setters[s_]["call"]:
        if c.get("lead_id") and (c.get("duration") or 0) >= 120:
            set_calls[c["lead_id"]].append(p(c["date_created"]))

# setter touches per lead (for confirmation)
setter_touch = defaultdict(list)
for s in setter_names:
    freq = Counter(norm(a.get("text")) for a in setters[s]["sms"])
    for a in setters[s]["sms"]:
        if a.get("status") not in ("sent", "delivered") or not a.get("lead_id"):
            continue
        t = a.get("text") or ""
        if freq[norm(t)] > 25 and not CALL_RE.search(t):
            continue
        setter_touch[a["lead_id"]].append((p(a["date_created"]), "sms", s, t))
    for c in setters[s]["call"]:
        if c.get("lead_id"):
            setter_touch[c["lead_id"]].append((p(c["date_created"]), "call", s, c.get("disposition")))

def closer_touches(d):
    freq = Counter(norm(a.get("text")) for a in d["sms"])
    by = defaultdict(list)
    for a in d["sms"]:
        t = a.get("text") or ""
        if a.get("status") not in ("sent", "delivered") or not a.get("lead_id") or BOOKING_RE.search(t):
            continue
        if freq[norm(t)] > 25 and not CALL_RE.search(t):
            continue
        by[a["lead_id"]].append((p(a["date_created"]), "sms"))
    for c in d["call"]:
        if c.get("lead_id"):
            by[c["lead_id"]].append((p(c["date_created"]), "call"))
    for e in d["email"]:
        if e.get("lead_id") and not e.get("sequence_id") and e.get("status") in (None, "sent"):
            by[e["lead_id"]].append((p(e.get("date_sent") or e["date_created"]), "email"))
    return by

def window_hits(touches, s, booked):
    sd = s.astimezone(ET).date()
    hit = set()
    for tup in touches:
        t = tup[0]
        if not t or t >= s - timedelta(minutes=10):
            continue
        if booked and t < booked + timedelta(hours=1):
            continue
        dd = t.astimezone(ET).date()
        if dd == sd:
            hit.add("dof")
        elif dd == sd - timedelta(days=1):
            hit.add("dbf")
    return hit

rows = []
for cl, d in closers.items():
    ct = closer_touches(d)
    seen = set()
    for m in d["meeting"]:
        s = p(m["starts_at"])
        if s >= NOW or not m.get("lead_id") or (m["lead_id"], m["starts_at"]) in seen:
            continue
        seen.add((m["lead_id"], m["starts_at"]))
        lead = m["lead_id"]
        booked = p(m.get("date_created"))
        # setter-set: a setter meeting or a "set to closer" call on this lead in the 21 days before booking (or up to 2h after)
        ref = booked or s
        lo, hi = ref - timedelta(days=21), ref + timedelta(hours=2)
        sm = [x for x in setter_mtgs.get(lead, []) if lo <= x[0] <= hi and x[0] < s]
        sc = [t for t in set_calls.get(lead, []) if lo <= t <= hi and t < s]
        route = "setter" if (sm or sc) else "direct"
        sd = s.astimezone(ET).date()
        o = eod.get((cl, sd.isoformat(), lead[-10:]))
        show = {"S": 1, "N": 0, "C": 0}.get(o)
        prior2 = bool(booked and booked.astimezone(ET).date() <= sd - timedelta(days=2))
        rows.append(dict(closer=cl, lead=lead, start=m["starts_at"], route=route, setter=(sm[0][1] if sm else None),
                         show=show, prior2=prior2,
                         c_hit=sorted(window_hits(ct.get(lead, []), s, booked)),
                         s_hit=sorted(window_hits(setter_touch.get(lead, []), s, booked))))

json.dump(rows, open(os.path.join(HERE, "split_rows.json"), "w"))

def rate(n, d):
    return f"{n}/{d} = {100*n/d:.0f}%" if d else "n/a"

print("closer | route | calls | show (S/(S+N+C)) | closer dof | closer dbf(2+d) | setter dof | setter dbf | any dof")
tot = defaultdict(Counter)
for cl in sorted(closers):
    for route in ("setter", "direct"):
        R = [r for r in rows if r["closer"] == cl and r["route"] == route]
        k = [r for r in R if r["show"] is not None]
        sh = sum(r["show"] for r in k)
        p2 = [r for r in R if r["prior2"]]
        c = Counter()
        c["calls"] = len(R); c["known"] = len(k); c["show"] = sh
        c["cdof"] = sum("dof" in r["c_hit"] for r in R)
        c["cdbf"] = sum("dbf" in r["c_hit"] for r in p2); c["p2"] = len(p2)
        c["sdof"] = sum("dof" in r["s_hit"] for r in R)
        c["sdbf"] = sum("dbf" in r["s_hit"] for r in p2)
        c["anydof"] = sum(("dof" in r["c_hit"]) or ("dof" in r["s_hit"]) for r in R)
        tot[route] += c
        print(f"{cl:8} {route:6} {c['calls']:4} | {rate(sh, len(k)):16} | {rate(c['cdof'], len(R)):15} | {rate(c['cdbf'], len(p2)):14} | {rate(c['sdof'], len(R)):14} | {rate(c['sdbf'], len(p2)):14} | {rate(c['anydof'], len(R))}")
for route, c in tot.items():
    print("TOTAL", route, c["calls"], "show", rate(c["show"], c["known"]), "closer dof", rate(c["cdof"], c["calls"]), "setter dof", rate(c["sdof"], c["calls"]), "setter dbf", rate(c["sdbf"], c["p2"]), "any dof", rate(c["anydof"], c["calls"]))

# show rate by confirmed vs not, per route (call level)
for route in ("setter", "direct"):
    for lab, f in (("any day-of touch", lambda r: ("dof" in r["c_hit"]) or ("dof" in r["s_hit"])),
                   ("any day-before touch", lambda r: ("dbf" in r["c_hit"]) or ("dbf" in r["s_hit"]))):
        R = [r for r in rows if r["route"] == route and r["show"] is not None]
        if lab.startswith("any day-before"):
            R = [r for r in R if r["prior2"]]
        a = [r for r in R if f(r)]; b = [r for r in R if not f(r)]
        print(route, lab, "confirmed", rate(sum(r["show"] for r in a), len(a)), "| not", rate(sum(r["show"] for r in b), len(b)))
