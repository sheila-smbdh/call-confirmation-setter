"""Offline: the 6-month closer-call table (May-Oct 2026), with a Zoom-based show result. No network.

Reads close/m6/meet/*.json (45-minute meetings) and the Close user list saved as close/m6/users.json.
Show rule (DECISIONS.md section 10): the call happened if anyone other than the closer, other staff, or a
notetaker bot joined the Zoom. Cancelled meetings (declined by org or lead, or cancelled) are left out of
show rates, because Close doesn't record when they were cancelled.
"""
import json, glob, os, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
M6 = os.path.join(HERE, "close", "m6")
NOW = datetime(2026, 11, 1, 4, 0, tzinfo=timezone.utc)
BOT_RE = re.compile(r"notetaker|read\.ai|fireflies|otter|fathom|tl;?dv|fyxer|\bbot\b|'s cal|recorder|assistant|meeting note", re.I)
CANCELLED = {"declined-by-org", "declined-by-lead", "canceled"}

p = lambda ts: datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def users():
    return {u["id"]: u for u in json.load(open(os.path.join(M6, "users.json")))["data"]}


def staff_names(us):
    out = set()
    for u in us.values():
        fn, ln = (u.get("first_name") or "").strip(), (u.get("last_name") or "").strip()
        if fn and ln:
            out.add(f"{fn} {ln}".lower())
    out |= {"owen james henderson", "vejohn c heinemann"}
    return out


def zoom_result(m, staff):
    """'show', 'noshow' (Zoom ran, no prospect joined), 'empty' (Zoom never started) or None (no Zoom data)."""
    z = [i for i in (m.get("integrations") or []) if i.get("integration_name") == "zoom"]
    if not z:
        return None
    parts = z[0].get("integration_data", {}).get("participants") or []
    if not parts:
        return "empty"
    for x in parts:
        n = (x.get("name") or "").strip()
        if not n or BOT_RE.search(n) or n.lower() in staff:
            continue
        return "show"
    return "noshow"


def load_calls():
    us = users()
    staff = staff_names(us)
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(M6, "meet", "*.json"))):
        for m in json.load(open(f))["data"]:
            s = p(m["starts_at"])
            if not m.get("lead_id") or s >= NOW:
                continue
            key = (m["lead_id"], m["starts_at"])
            if key in seen:
                continue
            seen.add(key)
            u = us.get(m["user_id"], {})
            z = zoom_result(m, staff)
            cancelled = m.get("status") in CANCELLED
            show = None if cancelled else {"show": 1, "noshow": 0}.get(z)  # "empty" (Zoom never started) is unknown: EOD splits it across every outcome
            att = [a for a in (m.get("attendees") or []) if not (a.get("email") or "").lower().endswith(("smbdealhunter.xyz", "smbdealhunter.com", "dylanhelen.com"))]
            rows.append(dict(id=m["id"], lead=m["lead_id"], user=m["user_id"], closer=u.get("first_name", "?") + " " + (u.get("last_name") or "")[:1],
                             start=s, date=s.astimezone(ET).date(), booked=p(m.get("date_created")), status=m.get("status"),
                             cancelled=cancelled, zoom=z, show=show,
                             accepted=any(a.get("status") == "yes" for a in att) if att else None))
    return rows
