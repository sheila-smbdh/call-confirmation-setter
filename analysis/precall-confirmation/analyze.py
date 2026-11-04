"""Offline analysis of saved Close JSON (no network). Pre-call confirmation behaviour per closer."""
import json, glob, os, re, sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
RAW = os.path.join(os.path.dirname(__file__), "close", "raw")
NOW = datetime(2026, 11, 3, 5, 0, tzinfo=timezone.utc)  # only calls before end of Nov 2 ET

def p(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None

data = defaultdict(lambda: defaultdict(list))
for f in glob.glob(os.path.join(RAW, "*.json")):
    name = os.path.basename(f)
    closer, typ = name.split("_")[:2]
    d = json.load(open(f))
    if d.get("cursor"):
        print("WARN truncated", name, file=sys.stderr)
    data[closer][typ].extend(d.get("data", []))

CALL_RE = re.compile(r"\b(call|zoom|today|tomorrow|tonight|meeting|confirm)\b", re.I)
BOOKING_RE = re.compile(r"accept the calendar invite|Just reading through your app|you'll see a few emails come through|leading up to our call, you'll be receiving emails", re.I)

def norm(t):
    t = re.sub(r"\b(Hey|Hi|Hello|Good morning|Morning)\s+\w+", r"\1 X", t or "")
    t = re.sub(r"\d{1,2}(:\d{2})?\s*(am|pm|AM|PM|a\.m\.|p\.m\.)?\s*(ET|EST|EDT|CT|PT|MT|CST|PST|MST)?", "#", t)
    return re.sub(r"\s+", " ", t).strip()[:90]

out = {}
for closer, d in sorted(data.items()):
    # dedupe meetings by lead + start
    mtgs = {}
    for m in d["meeting"]:
        s = p(m["starts_at"])
        if not m.get("lead_id") or s >= NOW:
            continue
        mtgs.setdefault((m["lead_id"], m["starts_at"]), m)
    textfreq = Counter(norm(a.get("text")) for a in d["sms"])
    subjfreq = Counter(norm(a.get("subject")) for a in d["email"])
    by_lead = defaultdict(list)
    for kind in ("sms", "call", "email"):
        for a in d[kind]:
            if a.get("lead_id"):
                a["_kind"] = kind
                a["_t"] = p(a.get("date_sent") or a.get("date_created"))
                by_lead[a["lead_id"]].append(a)
    stats = Counter()
    samples = defaultdict(Counter)
    examples = {}
    lead_times = defaultdict(list)
    for (lead, st), m in mtgs.items():
        s = p(st)
        sd = s.astimezone(ET).date()
        booked = p(m.get("date_created"))
        stats["calls"] += 1
        same_day_booking = not (booked and booked.astimezone(ET).date() <= sd - timedelta(days=2))
        if not same_day_booking:
            stats["calls_booked_prior_day"] += 1
        flags = set()
        for a in by_lead.get(lead, []):
            t = a["_t"]
            if not t or t >= s or (booked and t < booked):
                continue
            if booked and (t - booked).total_seconds() < 3600:
                stats[("booking", a["_kind"])] += 1
                continue
            if a["_kind"] == "sms" and a.get("status") not in ("sent", "delivered"):
                stats["unsent_sms"] += 1
                continue
            if a["_kind"] == "email" and a.get("status") not in (None, "sent"):
                continue
            ad = t.astimezone(ET).date()
            mins = (s - t).total_seconds() / 60
            txt0 = (a.get("text") or "") if a["_kind"] == "sms" else ""
            if a["_kind"] == "sms" and textfreq[norm(txt0)] > 25 and not CALL_RE.search(txt0):
                continue  # bulk campaign blast
            if a["_kind"] == "email" and not a.get("sequence_id") and subjfreq[norm(a.get("subject"))] > 25 and not CALL_RE.search(a.get("subject") or ""):
                continue
            if a["_kind"] == "sms" and BOOKING_RE.search(txt0):
                stats[("booking", "sms_late")] += 1
                continue
            if a["_kind"] == "email" and a.get("sequence_id"):
                w = "dayof" if ad == sd else "daybefore" if ad == sd - timedelta(days=1) else None
                if w:
                    flags.add((w, "auto_workflow_email"))
                continue
            if mins <= 10:
                continue  # at-start / "I'm on zoom" messages: reactive, not confirmation
            if ad == sd:
                when = "dayof"
            elif ad == sd - timedelta(days=1):
                when = "daybefore"
            else:
                continue
            k = a["_kind"]
            auto = bool(a.get("sequence_id") or a.get("template_id"))
            flags.add((when, k))
            flags.add((when, "any"))
            if k == "email" and a.get("sequence_id"):
                flags.add((when, "email_seq"))
            elif k == "email":
                flags.add((when, "email_manual"))
            if k == "sms":
                flags.add((when, "sms_template" if a.get("template_id") else "sms_manual"))
            if k == "call":
                flags.add((when, "call_connected" if (a.get("duration") or 0) >= 30 else "call_noconnect"))
            if when == "dayof":
                lead_times[k].append(mins)
            txt = a.get("text") if k == "sms" else (a.get("sequence_name") or a.get("subject")) if k == "email" else a.get("disposition")
            samples[(when, k)][norm(txt)] += 1
            examples.setdefault((when, k, norm(txt)), (txt or "")[:400])
        for fl in flags:
            stats[fl] += 1
        if ("daybefore", "any") in flags and not same_day_booking:
            stats["db_eligible_hit"] += 1
    out[closer] = dict(stats=stats, samples=samples, lead_times=lead_times, examples=examples)

def med(x):
    x = sorted(x)
    return round(x[len(x) // 2]) if x else None

for closer, o in out.items():
    s = o["stats"]; n = s["calls"] or 1; nb = s["calls_booked_prior_day"] or 1
    print(f"\n=== {closer}: {s['calls']} past 45-min calls ({s['calls_booked_prior_day']} booked 2+ days ahead)")
    for when in ("daybefore", "dayof"):
        den = nb if when == "daybefore" else n
        num = s["db_eligible_hit"] if when == "daybefore" else s[(when, "any")]
        print(f"  {when}: closer-own {num}/{den} = {100*num/den:.0f}% | auto-workflow-email {s[(when,'auto_workflow_email')]} | sms {s[(when,'sms')]} (manual {s[(when,'sms_manual')]}, tmpl {s[(when,'sms_template')]}) | call {s[(when,'call')]} (conn {s[(when,'call_connected')]}) | email {s[(when,'email')]} (seq {s[(when,'email_seq')]}, manual {s[(when,'email_manual')]})")
    print("  day-of median mins before call:", {k: med(v) for k, v in o["lead_times"].items()})
    for key in (("daybefore", "sms"), ("dayof", "sms"), ("dayof", "email"), ("daybefore", "email"), ("dayof", "call")):
        top = o["samples"][key].most_common(4)
        if top:
            print("  top", key, ":")
            for t, c in top:
                print(f"     {c:>3}x {o['examples'][(key[0], key[1], t)]!r}")
