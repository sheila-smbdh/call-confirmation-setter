"""Offline: 6-month (May-Oct 2026) pre-call confirmation vs show rate, setter-set vs direct. No network.

Inputs (all saved read-only pulls, never committed):
  close/m6/meet/*.json     45-minute closer meetings (with Zoom participants and invite responses)
  close/m6/setter/*.json   setter meetings (< 45 min) and setter calls of 2+ minutes, from Apr 10
  close/m6/touch/*.json    texts (both directions), calls and emails on those leads, day before -> call
  close/m6/users.json      Close users

Writes rows6.json (one row per call) and prints the tables used in the report.
"""
import json, glob, os, re, math, sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calls6 import load_calls, ET, M6, p  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SETTERS = {
    "user_rtKYgVTxSrwnTd5wJJA5Y6jr4gteTRTV1BloPCzuWXQ": "Gabriel",
    "user_sByZkVjk2If3ioL4CC26O5JmTWuzzKzDEjr9fzZHJ26": "Dave",
    "user_TH3XzqxRNb7WhZ5taaJ9v3df27VAaU6KvCnFlCUbq9v": "Yobani",
    "user_3IrYZLUcCBZrg2mb49wCybrxGBFTCxa5eqTHhE1ApuC": "Jordan K",
    "user_fXLAvRIRIJxMAgcaYa2hH14SuwQphwF5aC9vtvouHob": "Quinn",
    "user_c0wPSKtEPsqkIh08OnjiGaj6XHeFBjGSp2jyVxAggDl": "Bali",
    "user_msFtSHmZcoRAYvHX8aGrnygBzOy4u1GnLrRSFfIdcgk": "Jose",
}
OMAR = "user_KljJRbJ4KU5gr2vYuVcQOXr2fwDrBRWF77rHsqIvmTP"  # set 15-min calls in May before moving to closing
CLOSER_NAMES = {"Adam L", "Owen H", "VeJohn H", "Ezra I", "Jordan W", "Jordan Z", "Nick V", "Julien B", "Kameron B",
                "Chris C", "Giovana d", "Omar K", "Harry W", "Daniel J", "Kevin M", "Solomon H", "Tyler J", "Oliver E"}
LABEL = {"Ezra I": "EJ", "Jordan Z": "Jay Z", "Jordan W": "Jordan W", "Giovana d": "Giovana"}

BOOKING_RE = re.compile(r"accept the calendar invite|Just reading through your app|you'll see a few emails come through|leading up to our call, you'll be receiving emails", re.I)
CALL_RE = re.compile(r"\b(call|zoom|today|tomorrow|tonight|meeting|confirm)\b", re.I)


def norm(t):
    t = re.sub(r"\b(Hey|Hi|Hello|Good morning|Morning)\s+\w+", r"\1 X", t or "")
    t = re.sub(r"\d{1,2}(:\d{2})?\s*(am|pm|AM|PM)?\s*(ET|EST|EDT|CT|PT|MT|CST|PST|MST)?", "#", t)
    return re.sub(r"\s+", " ", t).strip()[:90]


def loadj(pattern):
    out = {}
    for f in glob.glob(os.path.join(M6, pattern)):
        for a in json.load(open(f)).get("data", []):
            out[a["id"]] = a
    return list(out.values())


# ---------------- calls
calls = [c for c in load_calls() if c["closer"] in CLOSER_NAMES]
for c in calls:
    c["closer"] = LABEL.get(c["closer"], c["closer"])

# ---------------- setter evidence (meeting with the lead, or a 2+ minute call, 21 days before booking to 2h after)
evidence = defaultdict(list)
for m in loadj("setter/meeting_*.json"):
    if not m.get("lead_id") or m.get("status") in ("declined-by-org", "declined-by-lead", "canceled"):
        continue
    if m["user_id"] == OMAR and not (m.get("duration") == 900 and m["starts_at"] < "2026-06-01"):
        continue
    who = SETTERS.get(m["user_id"], "Omar")
    evidence[m["lead_id"]].append((p(m["starts_at"]), who))
for c in loadj("setter/call_*.json"):
    if c.get("lead_id") and (c.get("duration") or 0) >= 120 and c["user_id"] in SETTERS:
        evidence[c["lead_id"]].append((p(c["date_created"]), SETTERS[c["user_id"]]))

# ---------------- touches
sms, tcall, email = loadj("touch/sms_*.json"), loadj("touch/call_*.json"), loadj("touch/email_*.json")
freq = Counter(norm(a.get("text")) for a in sms if a.get("direction") == "outbound")
inbound = defaultdict(list)
for a in sms:
    if a.get("direction") == "inbound" and a.get("lead_id"):
        inbound[a["lead_id"]].append(p(a["date_created"]))
for e in email:
    if e.get("direction") == "incoming" and e.get("lead_id"):
        inbound[e["lead_id"]].append(p(e.get("date_sent") or e["date_created"]))

touch = defaultdict(list)   # lead -> (time, user, kind, template?, text)
auto_email = defaultdict(list)
for a in sms:
    t = a.get("text") or ""
    if a.get("direction") != "outbound" or a.get("status") not in ("sent", "delivered") or not a.get("lead_id"):
        continue
    if BOOKING_RE.search(t) or (freq[norm(t)] > 25 and not CALL_RE.search(t)):
        continue
    touch[a["lead_id"]].append((p(a.get("date_sent") or a["date_created"]), a.get("user_id"), "sms", bool(a.get("template_id")), t))
for c in tcall:
    if c.get("direction") == "outbound" and c.get("lead_id"):
        touch[c["lead_id"]].append((p(c["date_created"]), c.get("user_id"), "call", False, c.get("disposition") or ""))
for e in email:
    if e.get("direction") != "outgoing" or not e.get("lead_id") or e.get("status") not in (None, "sent"):
        continue
    if e.get("sequence_id"):
        auto_email[e["lead_id"]].append(p(e.get("date_sent") or e["date_created"]))
    else:
        touch[e["lead_id"]].append((p(e.get("date_sent") or e["date_created"]), e.get("user_id"), "email", bool(e.get("template_id")), e.get("subject") or ""))


def when(t, c):
    """'dof' / 'dbf' / None for a touch at t on call c, using the October rules."""
    s, b = c["start"], c["booked"]
    if not t or t >= s - timedelta(minutes=10) or (b and t < b + timedelta(hours=1)):
        return None
    d, sd = t.astimezone(ET).date(), c["date"]
    return "dof" if d == sd else "dbf" if d == sd - timedelta(days=1) else None


def reactive(lead, t):
    return any(x and timedelta(0) <= t - x <= timedelta(hours=3) for x in inbound.get(lead, []))


rows = []
for c in calls:
    lead, ref = c["lead"], c["booked"] or c["start"]
    ev = [w for (t, w) in evidence.get(lead, []) if ref - timedelta(days=21) <= t <= ref + timedelta(hours=2) and t < c["start"]]
    hits, pro = set(), set()
    tmpl = set()
    for (t, u, kind, istmpl, txt) in touch.get(lead, []):
        w = when(t, c)
        if not w:
            continue
        role = "c" if u == c["user"] else "s" if u in SETTERS else None
        if not role:
            continue
        hits.add(role + w)
        if not reactive(lead, t):
            pro.add(role + w)
        if istmpl:
            tmpl.add(role + w)
    auto = {when(t, c) for t in auto_email.get(lead, [])} - {None}
    prior2 = bool(c["booked"] and c["booked"].astimezone(ET).date() <= c["date"] - timedelta(days=2))
    rows.append(dict(closer=c["closer"], month=c["date"].strftime("%Y-%m"), date=c["date"].isoformat(), lead=lead,
                     route="setter" if ev else "direct", setter=ev[0] if ev else None, show=c["show"], cancelled=c["cancelled"],
                     zoom=c["zoom"], accepted=c["accepted"], prior2=prior2, hit=sorted(hits), pro=sorted(pro), tmpl=sorted(tmpl),
                     auto=sorted(auto), lead_hours=round(((c["start"] - c["booked"]).total_seconds() / 3600) if c["booked"] else -1, 1)))
json.dump(rows, open(os.path.join(HERE, "rows6.json"), "w"))


# ---------------- stats helpers
def rate(rs):
    k = [r for r in rs if r["show"] is not None]
    n = sum(r["show"] for r in k)
    return n, len(k)


def fmt(rs):
    n, d = rate(rs)
    return f"{100*n/d:5.1f}% ({n}/{d})" if d else "   n/a"


def mh(rs, f, strata=lambda r: r["closer"]):
    """Show-rate difference (f true minus false) within closer, pooled Mantel-Haenszel style, with a z score."""
    by = defaultdict(lambda: [0, 0, 0, 0])
    for r in rs:
        if r["show"] is None:
            continue
        a = by[strata(r)]
        if f(r):
            a[0] += r["show"]; a[1] += 1
        else:
            a[2] += r["show"]; a[3] += 1
    num = den = var = 0.0
    for x1, n1, x0, n0 in by.values():
        if not n1 or not n0:
            continue
        w = n1 * n0 / (n1 + n0)
        p1, p0 = x1 / n1, x0 / n0
        num += w * (p1 - p0); den += w
        pp = (x1 + x0) / (n1 + n0)
        var += w * w * pp * (1 - pp) * (1 / n1 + 1 / n0)
    if not den:
        return "n/a"
    d = num / den
    se = math.sqrt(var) / den if var else float("nan")
    z = d / se if se else float("nan")
    pv = math.erfc(abs(z) / math.sqrt(2)) if se else float("nan")
    return f"{100*d:+5.1f} pts within-closer (95% CI {100*(d-1.96*se):+.1f} to {100*(d+1.96*se):+.1f}, p={pv:.3f})"


live = [r for r in rows if not r["cancelled"]]
known = [r for r in live if r["show"] is not None]
print(f"calls {len(rows)} | cancelled {sum(r['cancelled'] for r in rows)} | held-or-no-show with Zoom result {len(known)}")
print("months:", dict(sorted(Counter(r['month'] for r in known).items())))

print("\n== show rate by route")
for route in ("setter", "direct"):
    R = [r for r in live if r["route"] == route]
    print(f"{route:7} calls {len(R):5}  show {fmt(R)}")
print("by month:")
for m in sorted({r["month"] for r in rows}):
    print(" ", m, "setter", fmt([r for r in live if r["month"] == m and r["route"] == "setter"]),
          "| direct", fmt([r for r in live if r["month"] == m and r["route"] == "direct"]),
          "| setter share", f"{100*sum(r['route']=='setter' for r in rows if r['month']==m)/max(1,sum(r['month']==m for r in rows)):.0f}%")
print("setter-set calls by setter:", Counter(r["setter"] for r in rows if r["route"] == "setter").most_common())

H = lambda k: (lambda r: k in r["hit"])
P = lambda k: (lambda r: k in r["pro"])
print("\n== invite accepted")
for route in ("setter", "direct"):
    R = [r for r in live if r["route"] == route and r["accepted"] is not None]
    print(f"{route:7} accepted {fmt([r for r in R if r['accepted']])} | not {fmt([r for r in R if not r['accepted']])} | acceptance rate {100*sum(r['accepted'] for r in R)/max(1,len(R)):.0f}%")

for route in ("setter", "direct"):
    R = [r for r in live if r["route"] == route]
    R2 = [r for r in R if r["prior2"]]
    print(f"\n== {route.upper()} calls ({len(R)} live; {len(R2)} booked 2+ days ahead)")
    tests = [
        ("closer day-of (any)", R, H("cdof")), ("closer day-of (proactive)", R, P("cdof")),
        ("closer day-before (any)", R2, H("cdbf")), ("closer day-before (proactive)", R2, P("cdbf")),
    ]
    if route == "setter":
        tests += [
            ("setter day-of (any)", R, H("sdof")), ("setter day-of (proactive)", R, P("sdof")),
            ("setter day-before (any)", R2, H("sdbf")), ("setter day-before (proactive)", R2, P("sdbf")),
            ("any day-of", R, lambda r: "cdof" in r["hit"] or "sdof" in r["hit"]),
            ("any day-before", R2, lambda r: "cdbf" in r["hit"] or "sdbf" in r["hit"]),
        ]
    else:
        tests += [("auto email day-before", R2, lambda r: "dbf" in r["auto"])]
    for lab, RR, f in tests:
        a = [r for r in RR if f(r)]; b = [r for r in RR if not f(r)]
        print(f"  {lab:32} yes {fmt(a)} | no {fmt(b)} | {mh(RR, f)}")

S = [r for r in live if r["route"] == "setter"]
S2 = [r for r in S if r["prior2"]]


def pattern(r, ks):
    return "+".join(k for k in ks if k in r["hit"]) or "none"


print("\n== setter-set: day-of, who touched")
for k, v in sorted(Counter(pattern(r, ("sdof", "cdof")) for r in S).items()):
    print(f"  {k:12} {fmt([r for r in S if pattern(r, ('sdof','cdof')) == k])}")
print("== setter-set (booked 2+ days ahead): full pattern")
for k, v in sorted(Counter(pattern(r, ("sdbf", "sdof", "cdbf", "cdof")) for r in S2).items(), key=lambda x: -x[1]):
    print(f"  {k:24} {fmt([r for r in S2 if pattern(r, ('sdbf','sdof','cdbf','cdof')) == k])}")
prop = lambda r: {"sdbf", "sdof", "cdof"} <= set(r["hit"])
sdof_cdof = lambda r: {"sdof", "cdof"} <= set(r["hit"])
print("  proposed (setter dbf + setter dof + closer dof):", fmt([r for r in S2 if prop(r)]))
print("  setter dof + closer dof (any day-before):", fmt([r for r in S if sdof_cdof(r)]))
print("  setter dof, no closer dof:", fmt([r for r in S if "sdof" in r["hit"] and "cdof" not in r["hit"]]))
print("  closer dof, no setter dof:", fmt([r for r in S if "cdof" in r["hit"] and "sdof" not in r["hit"]]))
print("  neither:", fmt([r for r in S if "cdof" not in r["hit"] and "sdof" not in r["hit"]]))

print("\n== does a setter day-before touch go with invite acceptance? (setter-set, booked 2+ days ahead)")
A = [r for r in S2 if r["accepted"] is not None]
for lab, f in (("setter day-before", H("sdbf")), ("closer day-before", H("cdbf")), ("any day-before", lambda r: "sdbf" in r["hit"] or "cdbf" in r["hit"])):
    a = [r for r in A if f(r)]; b = [r for r in A if not f(r)]
    pa = sum(r["accepted"] for r in a) / max(1, len(a)); pb = sum(r["accepted"] for r in b) / max(1, len(b))
    print(f"  {lab:20} accepted {100*pa:.0f}% of {len(a)} | without {100*pb:.0f}% of {len(b)}")

print("\n== per closer (live calls): route mix, show, day-of rates")
for cl in sorted({r["closer"] for r in rows}):
    R = [r for r in live if r["closer"] == cl]
    Sx = [r for r in R if r["route"] == "setter"]; Dx = [r for r in R if r["route"] == "direct"]
    print(f"  {cl:9} calls {len(R):4} | setter {len(Sx):3} show {fmt(Sx)} | direct {len(Dx):4} show {fmt(Dx)} | closer dof {100*sum('cdof' in r['hit'] for r in R)/max(1,len(R)):.0f}% | setter dof on set {100*sum('sdof' in r['hit'] for r in Sx)/max(1,len(Sx)):.0f}%")
