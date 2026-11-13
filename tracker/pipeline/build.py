"""Offline: build confirmation tracker rows (v2) from saved Calendly / Close / Slack / EOD files. No network.

v2 rules (Sheila, Nov 12):
- Gino's queue = #call-confirmation "NEW CALL BOOKED" alerts + Close confirmation smart views (lead status
  "Needs Confirmation" / "Needs Confirmation - Reschedule"). Calendly/Close only find what's missing; calls that
  never reached his queue are shown but don't count toward his gate.
- Welcome calls split into Overnight (booked outside his shift, due first thing next shift) and During shift.
- A booking whose invite was accepted before the welcome call was due needs no welcome call.
- Invite accepted/declined times come from the calendar response emails ("Accepted:" / "Declined:") synced to Close.

Usage: python3 -I build.py DATA_DIR TODAY(YYYY-MM-DD, ET run date)  -> DATA_DIR/calls_new.json
Only the calls in DATA_DIR/scope.json are built (scope.py picks the run window); merge.py combines them with the rows
already in the tracker.
"""
import json, sys, glob, os
from datetime import datetime, timedelta, timezone, date, time
from zoneinfo import ZoneInfo

D = sys.argv[1]
ET = ZoneInfo("America/New_York")
GINO = "user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo"
CF = "custom.cf_9T3J6wVqEN7pPSv3evMHFsBrcZBeTYksCqkgkPHBokX"
TODAY = date.fromisoformat(sys.argv[2])
DAYS = [date(2026, 11, 10) + timedelta(days=i) for i in range((TODAY - date(2026, 11, 10)).days + 1)]
NO_GATE_DB = {date(2026, 11, 10)}          # Jay: welcome calls only on day 1
START = datetime(2026, 11, 10, 1, 0, tzinfo=timezone.utc)   # Nov 9 8pm ET
LAST_SHIFT_END = datetime.now(timezone.utc)  # bookings after this run are picked up by the next run
NC = {"Needs Confirmation", "Needs Confirmation - Reschedule"}

def p(s):
    if not s:
        return None
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

et = lambda d, h, m=0: datetime.combine(d, time(h, m), ET)
shift_start = lambda d: et(d, 11)
shift_end = lambda d: et(d, 20)
cutoff = lambda d: et(d, 19, 45)
workday = lambda d: d.weekday() < 5
fmt = lambda t: t.astimezone(ET).strftime("%b %-d %-I:%M %p") if t else ""

def in_shift(t):
    d = t.astimezone(ET).date()
    return workday(d) and shift_start(d) <= t < shift_end(d)

def next_shift_start(t):
    d = t.astimezone(ET).date()
    if workday(d) and t < shift_start(d):
        return shift_start(d)
    d += timedelta(days=1)
    while not workday(d):
        d += timedelta(days=1)
    return shift_start(d)

# ---------------- load ----------------
users = {u["id"]: u for u in json.load(open(f"{D}/users.json"))["data"]}
by_email = {(u.get("email") or "").lower(): u for u in users.values()}
OUT = {"outcome_034XYnwGD1sz2iKRzZAeuk": "Conversation: set to closer", "outcome_034XYnwGIwjSI4Lv7KMPpM": "Conversation: set to self",
       "outcome_034XYnwGOoIokD2rjyIqSz": "Conversation: call back later", "outcome_034XYnwGUtrbIzKcoCmgNC": "No Answer – Left Voicemail",
       "outcome_034XYnwGbBHD0PSnnDgREb": "Call screener: got through", "outcome_034XYnwGh7qMgdHgAzsDew": "No Answer – Automated System",
       "outcome_034XYnwGn0yTNuY7U8Xpr7": "No answer / hung up", "outcome_034XYnwGtB7ZxIflobLBJE": "Disqualified",
       "outcome_034XYnwGz4hLfW6ZZPC3FR": "Do Not Contact", "outcome_034anX5E9WxBi38puNw899": "No Answer – No VM Option",
       "outcome_034vmKpaEpoHxzXjckNwnb": "Conversation: Confirmed and Accepted", "outcome_034vmKpaL514fI05EqyM28": "Conversation: Confirmed not Accepted"}
scope = json.load(open(f"{D}/scope.json"))
inv = {}
for l in open(f"{D}/cal_invitees.jsonl"):
    x = json.loads(l)
    inv.setdefault(x["event_uri"], []).append(x)
M = {}
for f in sorted(os.path.basename(x) for x in glob.glob(f"{D}/meet_*.json")):
    for m in json.load(open(f"{D}/{f}"))["data"]:
        M[m["id"]] = m
allcalls = list({c["id"]: c for f in sorted(glob.glob(f"{D}/g_call*.json")) for c in json.load(open(f))["data"]}.values())
calls = sorted([c for c in allcalls if c["direction"] == "outbound"], key=lambda c: c["date_created"])
inbound = [c for c in allcalls if c["direction"] == "inbound" and c.get("disposition") == "answered" and (c.get("duration") or 0) >= 45]
allsms = list({x["id"]: x for f in sorted(glob.glob(f"{D}/g_sms*.json")) for x in json.load(open(f))["data"]}.values())
sms = [s for s in allsms if s["direction"] == "outbound"]
fev = sorted({e["id"]: e for f in sorted(glob.glob(f"{D}/g_ev*.json")) for e in json.load(open(f))["data"] if CF in e["changed_fields"]}.values(), key=lambda e: e["date_updated"])
fval = lambda e: ((e.get("data") or {}).get(CF) or [""])[0]
eod = {}
for f in sorted(glob.glob(f"{D}/eod*.json")):
    eod.update(json.load(open(f)))
optional = lambda name: json.load(open(f"{D}/{name}")) if os.path.exists(f"{D}/{name}") else {}
lead_fix = optional("lead_fix.json")
overrides = optional("overrides.json")
alerts = [json.loads(l) for l in open(f"{D}/slack_alerts.jsonl")]
booked_alerts = [a for a in alerts if a["type"] == "NEW CALL BOOKED"]
for a in booked_alerts:
    a["t"] = datetime.strptime(a["posted_at_et"], "%Y-%m-%d %H:%M").replace(tzinfo=ET)
alert_leads = {a["lead_id"] for a in booked_alerts}
lsc = {}
for f in sorted(glob.glob(f"{D}/lsc_*.json")):
    for x in json.load(open(f))["data"]:
        lsc[x["id"]] = x
status_changes = {}
for x in lsc.values():
    status_changes.setdefault(x["lead_id"], []).append((p(x["date_created"]), x.get("old_status_label"), x.get("new_status_label"), x.get("user_id")))
for v in status_changes.values():
    v.sort(key=lambda r: r[0])
resp = {}
for f in sorted(glob.glob(f"{D}/acc_*.json")):
    for x in json.load(open(f))["data"]:
        s = (x.get("subject") or "").lower()
        k = "D" if s.startswith("declined") else ("T" if s.startswith("tentatively") else "A")
        resp.setdefault(x["lead_id"], []).append((p(x["date_created"]), k))
for v in resp.values():
    v.sort()
gino_leads = {c["lead_id"] for c in calls} | {s["lead_id"] for s in sms}

BOTS = ("notetaker", "read.ai", "fireflies", "otter", "fathom", "tldv", "fyxer", " bot", "'s cal", "recorder", "assistant", "meeting note")
staff = {f"{(u.get('first_name') or '').strip()} {(u.get('last_name') or '').strip()}".lower() for u in users.values()} | {"owen james henderson", "vejohn c heinemann"}
STAFF_DOM = ("smbdealhunter.xyz", "smbdealhunter.com", "dylanhelen.com")

def zoom(m):
    z = [i for i in (m.get("integrations") or []) if i.get("integration_name") == "zoom"]
    if not z:
        return None
    parts = z[0].get("integration_data", {}).get("participants") or []
    if not parts:
        return "Zoom never started"
    for x in parts:
        n = (x.get("name") or "").strip()
        if n and not any(b in n.lower() for b in BOTS) and n.lower() not in staff:
            return "Showed (Zoom)"
    return "No-show (Zoom)"

def status_at(lead, t):
    ch = status_changes.get(lead, [])
    before = [c for c in ch if c[0] <= t]
    if before:
        return before[-1][2], before[-1][3]
    after = [c for c in ch if c[0] > t]
    return (after[0][1], None) if after else (None, None)

def accepted_by(lead, t, lo):
    """True/False from the last calendar response between lo and t; None if none."""
    rs = [k for (ts, k) in resp.get(lead, []) if lo <= ts <= t]
    return None if not rs else rs[-1] == "A"

def first_accept(lead, lo, hi):
    return next((ts for ts, k in resp.get(lead, []) if lo <= ts <= hi and k == "A"), None)

def gino_claims(lead, lo, hi):
    """Times Gino recorded the invite as accepted: field 1/3, outcome Confirmed and Accepted, status -> Confirmed."""
    out = []
    for e in fev:
        if e["lead_id"] == lead and lo <= p(e["date_updated"]) <= hi and fval(e).startswith(("1.", "3.")):
            out.append((p(e["date_updated"]), "field " + fval(e)[:2]))
    for c in calls:
        if c["lead_id"] == lead and lo <= p(c["date_created"]) <= hi and OUT.get(c.get("outcome_id")) == "Conversation: Confirmed and Accepted":
            out.append((p(c["date_created"]), "outcome"))
    for ts, old, new, uid in status_changes.get(lead, []):
        if uid == GINO and new == "Confirmed" and lo <= ts <= hi:
            out.append((ts, "status Confirmed"))
    return sorted(out)

def is_vm(c):
    return OUT.get(c.get("outcome_id")) == "No Answer – Left Voicemail" or c.get("disposition") == "vm-left" or bool(c.get("voicemail_url"))

def is_conn(c):
    o = OUT.get(c.get("outcome_id"), "")
    if o.startswith("Conversation") or o == "Call screener: got through":
        return True
    return not o and c.get("disposition") == "answered" and (c.get("duration") or 0) >= 45 and not is_vm(c)

def checkpoint(lead, lo, hi, due):
    cs = [c for c in calls if c["lead_id"] == lead and lo <= p(c["date_created"]) < hi]
    sent = [s for s in sms if s["lead_id"] == lead and lo <= p(s["date_created"]) < hi and s["status"] in ("sent", "delivered")]
    cb = [c for c in inbound if c["lead_id"] == lead and lo <= p(c["date_created"]) < hi]
    r = dict(dials=len(cs), first_dial=p(cs[0]["date_created"]) if cs else None, touched=bool(cs))
    r["connected"] = any(is_conn(c) for c in cs) or bool(cb)
    first_conn = bool(cs) and is_conn(cs[0])
    dd = any(p(b["date_created"]) - p(a["date_created"]) <= timedelta(minutes=3) for a, b in zip(cs, cs[1:]))
    r["double_dial"] = "N/A (answered first dial)" if first_conn else ("Yes" if dd else ("No" if cs else ""))
    r["voicemail"] = any(is_vm(c) for c in cs)
    r["text"] = bool(sent)
    # Can't-do exceptions: no voicemail box (or full) logged as the "No VM Option" outcome; a text Close couldn't send.
    vm_x = not r["voicemail"] and any(OUT.get(c.get("outcome_id")) == "No Answer – No VM Option" for c in cs)
    tx_x = not r["text"] and any(s["lead_id"] == lead and lo <= p(s["date_created"]) < hi and s["status"] in ("error", "failed", "undelivered")
                                 for s in allsms)
    if not cs:
        r["finished"], r["dropoff"] = False, "Not touched"
    elif r["connected"]:
        r["finished"], r["dropoff"] = True, ""
    else:
        miss = [n for n, ok in (("double dial", dd), ("voicemail", r["voicemail"] or vm_x), ("text", r["text"] or tx_x)) if not ok]
        r["finished"], r["dropoff"] = not miss, ("Missing " + ", ".join(miss)) if miss else ""
    if vm_x:
        r["voicemail"] = "No VM option"
    if tx_x:
        r["text"] = "Text failed to send"
    r["on_time"] = bool(cs) and r["first_dial"] <= due
    return r

def queue_check(lead, t):
    """Was this call in Gino's day-before / 5:45 view at time t? Returns (counts, label)."""
    st, uid = status_at(lead, t)
    gino_acc = any(e["lead_id"] == lead and p(e["date_updated"]) <= t and fval(e).startswith(("1.", "3.")) for e in fev)
    if st in NC and not gino_acc:
        return True, "In his smart view"
    if (st == "Confirmed" and uid == GINO) or gino_acc:
        cl = gino_claims(lead, t - timedelta(days=14), t)
        if cl and accepted_by(lead, cl[0][0] + timedelta(minutes=15), cl[0][0] - timedelta(days=14)) is True:
            return False, "Not in his queue: he correctly logged it accepted, the prospect declined later"
        return True, "Out of his view because he logged it accepted when it wasn't"
    return False, f"Not in his queue (lead status: {st or 'unknown'})"

# ---------------- rows ----------------
rows = []
for ev in scope:
    i = (inv.get(ev["uri"]) or [{}])[0]
    s, booked = p(ev["start"]), p(ev["created"])
    cands = {}
    for mid, lid, st, title in ev["close"]:
        cands.setdefault(lid, mid)
    email = (i.get("email") or "").lower()
    mail_alert = [a for a in booked_alerts if (a.get("lead_email") or "").lower() == email]
    by_mail = [l for l, mid in cands.items() if email and any((a_.get("email") or "").lower() == email for a_ in (M.get(mid) or {}).get("attendees") or [])]
    lead = (lead_fix.get(ev["uri"])
            or (by_mail[0] if len(by_mail) == 1 else None)
            or next((l for l in by_mail if l in alert_leads), None)
            or next((l for l in cands if l in alert_leads), None)
            or (next(iter(cands)) if len(cands) == 1 else None)
            or next((l for l in cands if l in gino_leads), None)
            or (mail_alert[0]["lead_id"] if mail_alert else None))
    meet = M.get(cands.get(lead)) if lead in cands else None
    host = by_email.get(ev["host"], {})
    closer = f"{host.get('first_name', '')} {host.get('last_name', '')}".strip() or ev["host"]
    tz = i.get("timezone") or ""
    cancel_at = p(ev["canceled_at"]) if ev["status"] == "canceled" else None
    resched = bool(i.get("rescheduled"))
    att = [a for a in ((meet or {}).get("attendees") or []) if not (a.get("email") or "").lower().endswith(STAFF_DOM)]
    acc_now = any(a.get("status") == "yes" for a in att) if att else None
    declined_now = any(a.get("status") == "no" for a in att) if att else None
    cd = s.astimezone(ET).date()
    alive_until = cancel_at or s
    lo_resp = booked - timedelta(minutes=1)
    rs_window = [(ts, k) for ts, k in resp.get(lead, []) if lo_resp <= ts <= s]
    row = dict(event=ev["uri"].rsplit("/", 1)[-1], lead_id=lead or "", lead_name=(i.get("name") or "").strip(), email=email,
               closer=closer, call_date=cd.isoformat(), call_et=s.astimezone(ET).strftime("%-I:%M %p"),
               call_local=(s.astimezone(ZoneInfo(tz)).strftime("%-I:%M %p ") + s.astimezone(ZoneInfo(tz)).tzname()) if tz else "",
               lead_tz=tz, booked_date=booked.astimezone(ET).date().isoformat(), booked_et=booked.astimezone(ET).strftime("%-I:%M %p"),
               booking_type="During shift" if in_shift(booked) else "Overnight",
               calendly_status=("Rescheduled" if resched else "Cancelled") if ev["status"] == "canceled" else "Active",
               cancelled_at_et=cancel_at.astimezone(ET).strftime("%Y-%m-%d %-I:%M %p") if cancel_at else "",
               cancelled_by=(ev.get("canceled_by") or "") if cancel_at else "",
               invite_now={True: "Accepted", False: ("Declined" if declined_now else "Not accepted"), None: "No Close meeting"}[acc_now],
               accepted_at=fmt(first_accept(lead, lo_resp, s)),
               declined_at=fmt(next((ts for ts, k in rs_window if k == "D"), None)))

    # ---- queue (Slack alert / smart view status) for the booking ----
    win_lo, win_hi = booked - timedelta(minutes=15), booked + timedelta(hours=3)
    in_slack = any(win_lo <= a["t"] <= win_hi and (a["lead_id"] == lead or (a.get("lead_email") or "").lower() == email) for a in booked_alerts)
    in_view = any(win_lo <= ts <= win_hi and new in NC for ts, old, new, uid in status_changes.get(lead, []))
    row["queue"] = "Slack + smart view" if in_slack and in_view else ("Slack only" if in_slack else ("Smart view only" if in_view else "Not in his queue"))

    # ---- welcome call ----
    row["w"] = None
    if booked < START:
        row["w_required"], row["w_reason"] = "No", "Booked before his first shift"
    elif booked >= LAST_SHIFT_END:
        row["w_required"], row["w_reason"] = "No", "Booked after the Nov 11 shift"
    else:
        if row["booking_type"] == "During shift":
            due, base = booked + timedelta(minutes=15), booked
        else:
            base = next_shift_start(booked)
            due = base + timedelta(minutes=30)
        row["w_due"] = due
        hi = min(alive_until, shift_end(due.astimezone(ET).date()))
        cp = checkpoint(lead, booked, hi, due)
        acc_t = first_accept(lead, lo_resp, s)
        claims = gino_claims(lead, booked, hi)
        if due.astimezone(ET).date() not in DAYS:
            row["w_required"], row["w_reason"] = "No", "Due after Nov 11"
        elif alive_until <= base:
            row["w_required"], row["w_reason"] = "No", "Call or cancel happened before his shift"
        elif acc_t and acc_t <= due and (not cp["first_dial"] or acc_t <= cp["first_dial"]):
            row["w_required"], row["w_reason"] = "Accepted at booking", "Invite accepted before the welcome call was due"
        elif (not rs_window and acc_now and claims and not cp["touched"]
              and any(c[1] == "status Confirmed" for c in claims)):
            row["w_required"], row["w_reason"] = "Accepted at booking", "Marked Confirmed by Gino, calendar shows accepted (time not recorded)"
        elif row["queue"] == "Not in his queue":
            row["w_required"], row["w_reason"] = "Not in his queue", "No Slack alert and never reached a confirmation smart view"
        else:
            row["w_required"] = "Yes"
            row["w_reason"] = "During shift: booking + 15 min" if row["booking_type"] == "During shift" else "Overnight: next shift start + 30 min"
        if row["w_required"] == "Yes":
            row["w"] = cp
            row["w_speed_min"] = round((cp["first_dial"] - base).total_seconds() / 60) if cp["first_dial"] else None

    # ---- day-before call ----
    db = cd - timedelta(days=1)
    while not workday(db):          # weekend calls: the day-before work happens on the last weekday before them
        db -= timedelta(days=1)
    row["db_date"] = db.isoformat()
    row["db"] = None
    def need(t):
        a = accepted_by(lead, t, lo_resp)
        if a is True:
            return "No", "Invite already accepted"
        if a is None and acc_now:
            return "Can't tell", "Accepted now, no calendar response email to show when"
        return "Yes", "Invite not accepted"
    if db not in DAYS:
        row["db_required"] = row["r_required"] = "No"
        row["db_reason"] = row["r_reason"] = "Day before is not Nov 10 or 11"
    else:
        if booked >= shift_start(db):
            row["db_required"], row["db_reason"] = "No", "Booked on the day before: welcome call covers it"
        elif cancel_at and cancel_at < shift_start(db):
            row["db_required"], row["db_reason"] = "No", "Cancelled or rescheduled before the day before"
        else:
            row["db_required"], row["db_reason"] = need(shift_start(db))
            if row["db_required"] == "Yes":
                ok, lab = queue_check(lead, shift_start(db))
                if not ok:
                    row["db_required"], row["db_reason"] = "Not in his queue", lab
                elif lab != "In his smart view":
                    row["db_reason"] = "Invite not accepted. " + lab
        if row["db_required"] in ("Yes", "Can't tell"):
            row["db"] = checkpoint(lead, et(db, 0), min(cutoff(db), alive_until), cutoff(db))
        # ---- 5:45 resolution ----
        if booked >= cutoff(db):
            row["r_required"], row["r_reason"] = "No", "Booked after 5:45 MT"
        elif cancel_at and cancel_at < cutoff(db):
            row["r_required"], row["r_reason"] = "No", "Cancelled or rescheduled before 5:45 MT"
        else:
            row["r_required"], row["r_reason"] = need(cutoff(db))
            if row["r_required"] == "Yes":
                row["r_reason"] = "Not accepted at 5:45 MT" + (" (booked that same day)" if booked >= shift_start(db) else "")
                ok, lab = queue_check(lead, cutoff(db))
                if not ok:
                    row["r_required"], row["r_reason"] = "Not in his queue", lab
        if row["r_required"] in ("Yes", "Can't tell"):
            by_gino = bool(cancel_at) and "gino" in (ev.get("canceled_by") or "").lower()
            field6 = any(e["lead_id"] == lead and fval(e).startswith("6.") for e in fev)
            if cancel_at and cancel_at.astimezone(ET).date() == db and (by_gino or field6):
                row["r_result"] = "Cancelled"
            elif cancel_at and cancel_at.astimezone(ET).date() == cd and (by_gino or field6):
                row["r_result"] = "Cancelled on the day of the call"
            elif cancel_at and cancel_at.astimezone(ET).date() == db:
                row["r_result"] = f"Cancelled by {ev.get('canceled_by')}"
            else:
                row["r_result"] = "Not cancelled"
    row["db_counts"] = "Yes" if row["db_required"] == "Yes" and db not in NO_GATE_DB else "No"
    row["r_counts"] = "Yes" if row["r_required"] == "Yes" and db not in NO_GATE_DB else "No"

    # ---- Gino's logging ----
    fv = [e for e in fev if e["lead_id"] == lead]
    row["last_field"] = fval(fv[-1]) if fv else ""
    lc = [OUT.get(c.get("outcome_id"), "") for c in calls if c["lead_id"] == lead and c.get("outcome_id")]
    row["last_outcome"] = lc[-1] if lc else ""
    gst = [(ts, new) for ts, old, new, uid in status_changes.get(lead, []) if uid == GINO]
    row["gino_status"] = f"{gst[-1][1]} ({fmt(gst[-1][0])})" if gst else ""
    claims = gino_claims(lead, booked, LAST_SHIFT_END + timedelta(days=1))
    row["check"] = ""
    if claims and ev["status"] != "canceled":
        tc = claims[0][0]
        a = accepted_by(lead, tc + timedelta(minutes=15), lo_resp)
        no_call = not any(c["lead_id"] == lead and booked <= p(c["date_created"]) <= tc + timedelta(minutes=5) for c in calls)
        if a is True:
            row["check"] = ("Verified: marked Confirmed without a call; invite was already accepted" if no_call
                            else "Verified: invite accepted when he logged it")
        elif lead in overrides:
            row["check"] = overrides[lead]
        elif a is None and acc_now:
            row["check"] = "Verified: calendar shows accepted (no response email to time it)"
        else:
            row["check"] = "Logging error: invite not accepted when he logged it (check the call transcript)"
        later_d = [ts for ts, k in rs_window if k == "D" and ts > tc]
        if later_d:
            row["check"] += f". Prospect later declined the invite ({fmt(later_d[0])})"
    # ---- did the call happen ----
    if cd > DAYS[-1]:
        row["happened"], row["happened_src"] = "Upcoming", ""
    elif cancel_at and cancel_at < s:
        row["happened"], row["happened_src"] = ("Rescheduled" if resched else "Cancelled"), "Calendly"
    elif f"{cd}|{lead}" in eod:
        row["happened"], row["happened_src"] = eod[f"{cd}|{lead}"][0], "#closer-eod"
    elif meet and zoom(meet):
        row["happened"], row["happened_src"] = zoom(meet), "Close (Zoom)"
    else:
        row["happened"], row["happened_src"] = "Unknown", "Ask Sheila"
    rows.append(row)

json.dump(rows, open(f"{D}/calls_new.json", "w"), default=str, indent=1)
print(len(rows), "rows")
