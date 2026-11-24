"""Offline: build the call recovery rows (one per lost call) from saved Close / Calendly / Slack files. No network.

Usage: python3 -I recovery.py DATA_DIR TODAY
  -> DATA_DIR/rec_rows.json      one row per lost call ("case"), for the Recovery tab
     DATA_DIR/rec_daily.json     per-day numbers, for the Daily tab and the scorecard
     DATA_DIR/rec_reviews.json   misses and logging errors, for the Reviews tab (coaching only; never change the bonus)
     DATA_DIR/need_rec_cal.txt   rebooked leads whose Calendly booking still has to be looked up (lead_id, email, from)

Rules (Sheila, Nov 23-24; decisions log rev 9):
- A row starts when a lead lands in a recovery status (No Show / Cancelled / Reschedule Request - Recovery), including
  Gino's own 5:45 day-before cancels. Leads he logged a Call Recovery day on with no such status change since REC_FROM
  are backlog rows, starting at his first call.
- The 5 business days start at his first attempt. Day 1, 3 and 5: double dial + voicemail + text unless he reaches
  them. Days 2 and 4: double dial unless he reaches them. Steps he can't do (no voicemail option, hung up before the
  voicemail, a dial that never rang, a text that won't send) aren't misses. Ends early on a rebook or "Not Interested".
  An open task of his on the lead pauses it until the task's date.
- Reschedule requests that land during his shift: first call within 15 minutes is tracked. Overnight: no speed target.
- Credit: he touched the lead after it landed in recovery and before the rebook, the rebook is on the closers' round
  robin (Calendly event type O2C), and Calendly names him as the scheduler (invitee_scheduled_by). Pays $50 when the
  lead shows, once per original lost call (a rebook that no-shows reopens the same chain).
- Nothing here gates the bonus. Misses go to Reviews for coaching.
Inputs (all optional except users.json): rec_lsc*, rec_field*, rec_act*, rec_info*, rec_calls*, rec_sms*, rec_meet*,
rec_tasks* (Close searches, see bodies.py), rec_cal.jsonl (Calendly lookups), eod*.json, g_ev*.json, rec_prev.json
(rows already on the tracker, from merge.py), rec_overrides.json ({"<review key>": "<verified reason>"}).
"""
import glob, json, os, sys
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

D = sys.argv[1]
TODAY = date.fromisoformat(sys.argv[2])
ET = ZoneInfo("America/New_York")
GINO = "user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo"
GINO_CAL = "https://api.calendly.com/users/a657209b-e5aa-4e23-b2e8-d9699363b19b"
O2C = "f144e281-c368-4a93-8897-9f0bee45f09e"       # closers' round robin, sdrb_c2_startnow
SCORE_FROM = date(2026, 11, 24)                     # recovery is tracked and counts for the bonus from here
REC_CF = "custom.cf_Cp9QRtPjlRz2XS2F7cDd4grwWbowcFYPjACyENQKvUT"
TYPE = {"No Show - Recovery": "No-show", "Cancelled - Recovery": "Cancel", "Reschedule Request - Recovery": "Reschedule request"}
BONUS = 50
OUT = {"outcome_034XYnwGD1sz2iKRzZAeuk": "Conversation", "outcome_034XYnwGIwjSI4Lv7KMPpM": "Conversation",
       "outcome_034XYnwGOoIokD2rjyIqSz": "Conversation", "outcome_034XYnwGUtrbIzKcoCmgNC": "No Answer – Left Voicemail",
       "outcome_034XYnwGbBHD0PSnnDgREb": "Call screener: got through", "outcome_034XYnwGn0yTNuY7U8Xpr7": "No answer / hung up",
       "outcome_034anX5E9WxBi38puNw899": "No Answer – No VM Option", "outcome_034vmKpaEpoHxzXjckNwnb": "Conversation",
       "outcome_034vmKpaL514fI05EqyM28": "Conversation", "outcome_034XYnwGtB7ZxIflobLBJE": "Conversation",
       "outcome_034XYnwGz4hLfW6ZZPC3FR": "Conversation"}

def p(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

et = lambda d, h, m=0: datetime.combine(d, time(h, m), ET)
workday = lambda d: d.weekday() < 5
fmt = lambda t: t.astimezone(ET).strftime("%a %b %-d %-I:%M%p").replace("AM", "am").replace("PM", "pm") if t else ""

def in_shift(t):
    d = t.astimezone(ET).date()
    return workday(d) and et(d, 11) <= t < et(d, 20)

def bdays(d0, n):
    out, d = [], d0
    while len(out) < n:
        if workday(d):
            out.append(d)
        d += timedelta(days=1)
    return out

def load(prefix):
    out = {}
    for f in sorted(glob.glob(f"{D}/{prefix}*.json")):
        for x in json.load(open(f)).get("data", []):
            out[x["id"]] = x
    return list(out.values())

opt = lambda n, d: json.load(open(f"{D}/{n}")) if os.path.exists(f"{D}/{n}") else d
users = {u["id"]: u for u in json.load(open(f"{D}/users.json"))["data"]}
uname = lambda uid: f"{users.get(uid, {}).get('first_name') or ''} {users.get(uid, {}).get('last_name') or ''}".strip() or "someone"
lsc = sorted(load("rec_lsc"), key=lambda x: x["date_created"])
field_leads = {x["id"] for x in load("rec_field")}
acts = load("rec_act")
info = {x["id"]: x for x in load("rec_info")}
calls = sorted(load("rec_calls"), key=lambda c: c["date_created"])
sms = sorted(load("rec_sms"), key=lambda s: s["date_created"])
meets = sorted(load("rec_meet"), key=lambda m: m["date_created"])
tasks = load("rec_tasks")
cal = [json.loads(l) for l in open(f"{D}/rec_cal.jsonl")] if os.path.exists(f"{D}/rec_cal.jsonl") else []
eod = {}
for f in sorted(glob.glob(f"{D}/eod*.json")):
    eod.update(json.load(open(f)))
fev = sorted({e["id"]: e for f in sorted(glob.glob(f"{D}/g_ev*.json")) for e in json.load(open(f))["data"]
              if REC_CF.replace("custom.", "custom.") in e.get("changed_fields", []) or REC_CF in e.get("changed_fields", [])}.values(),
             key=lambda e: e["date_updated"])
FEV_FROM = TODAY - timedelta(days=3)                 # g_ev covers Gino's lead updates from T-4 05:00 UTC
prev = opt("rec_prev.json", {})
overrides = opt("rec_overrides.json", {})
now = datetime.now(timezone.utc)

g_out = lambda lead, lo, hi: [c for c in calls if c["lead_id"] == lead and c["user_id"] == GINO and c["direction"] == "outbound" and lo <= p(c["date_created"]) < hi]
g_in = lambda lead, lo, hi: [c for c in calls if c["lead_id"] == lead and c["direction"] == "inbound" and c.get("disposition") == "answered"
                            and (c.get("duration") or 0) >= 45 and lo <= p(c["date_created"]) < hi]
g_sms = lambda lead, lo, hi: [s for s in sms if s["lead_id"] == lead and s["user_id"] == GINO and s["direction"] == "outbound" and lo <= p(s["date_created"]) < hi]

def is_vm(c):
    return OUT.get(c.get("outcome_id")) == "No Answer – Left Voicemail" or c.get("disposition") == "vm-left" or bool(c.get("voicemail_url"))

def is_conn(c):
    o = OUT.get(c.get("outcome_id"), "")
    if o in ("Conversation", "Call screener: got through"):
        return True
    return not o and c.get("disposition") == "answered" and (c.get("duration") or 0) >= 45 and not is_vm(c)

def vm_excused(cs):
    for c in cs:
        if OUT.get(c.get("outcome_id")) == "No Answer – No VM Option":
            return "No VM option"
        if c.get("disposition") == "answered" and not is_vm(c) and not is_conn(c) and ((c.get("duration") or 0) < 30 or OUT.get(c.get("outcome_id")) == "No answer / hung up"):
            return "Hung up before voicemail"
        if (c.get("disposition") in ("busy", "blocked", "error") or c.get("status") in ("busy", "failed")) and not (c.get("duration") or 0):
            return "Didn't ring"
    return None

def day_check(lead, d, k):
    lo, hi = et(d, 0), et(d + timedelta(days=1), 2)          # to midnight MT (Sheila, Nov 20)
    cs, sent = g_out(lead, lo, hi), [s for s in g_sms(lead, lo, hi) if s["status"] in ("sent", "delivered")]
    failed = [s for s in g_sms(lead, lo, hi) if s["status"] in ("error", "failed", "undelivered")]
    r = {"date": d.isoformat(), "day": k, "dials": len(cs)}
    if not cs:
        r.update(done=False, what="Not called")
        return r
    if any(is_conn(c) for c in cs) or g_in(lead, lo, hi):
        r.update(done=True, what="reached")
        return r
    first_conn = is_conn(cs[0])
    dd = first_conn or any(p(b["date_created"]) - p(a["date_created"]) <= timedelta(minutes=3) for a, b in zip(cs, cs[1:]))
    need = k in (1, 3, 5)
    vm = any(is_vm(c) for c in cs)
    vmx = None if vm else vm_excused(cs)
    miss = [n for n, ok in (("double dial", dd), ("voicemail", not need or vm or vmx), ("text", not need or sent or failed)) if not ok]
    parts = ["dd" if dd else "1 dial"] + (["VM" if vm else (vmx or "no VM"), "text" if sent else ("text failed" if failed else "no text")] if need else [])
    r.update(done=not miss, what=("+".join(parts) if not miss else "Missing " + ", ".join(miss)))
    return r

def paused(lead, d):
    for t in tasks:
        if t["lead_id"] == lead and t.get("assigned_to") == GINO and p(t["date_created"]).astimezone(ET).date() <= d < (p(t.get("date")) or now).astimezone(ET).date():
            return (p(t.get("date")) or now).astimezone(ET).date()
    return None

def zoom(m):
    z = [i for i in (m.get("integrations") or []) if i.get("integration_name") == "zoom"]
    if not z:
        return None
    parts = z[0].get("integration_data", {}).get("participants") or []
    if not parts:
        return "Zoom never started"
    staff = {f"{(u.get('first_name') or '').strip()} {(u.get('last_name') or '').strip()}".lower() for u in users.values()}
    bots = ("notetaker", "read.ai", "fireflies", "otter", "fathom", "tldv", "fyxer", " bot", "'s cal", "recorder", "assistant", "meeting note")
    for x in parts:
        n = (x.get("name") or "").strip()
        if n and not any(b in n.lower() for b in bots) and n.lower() not in staff:
            return "Showed (Zoom)"
    return "No-show (Zoom)"

def email_of(lead):
    for c in (info.get(lead, {}).get("contacts") or []):
        for e in c.get("emails") or []:
            if e.get("email"):
                return e["email"].lower()
    return ""

# ---------------- rows ----------------
rows, by_lead = [], {}
def new_row(lead, start, typ, found_by, chain=None, rebook_no=0):
    r = dict(id=f"{lead}|{start.isoformat()}", lead_id=lead, lead_name=info.get(lead, {}).get("display_name") or lead, type=typ,
             found_by=found_by, start=start.isoformat(), chain=chain or f"{lead}|{start.isoformat()}", rebook_no=rebook_no)
    rows.append(r)
    by_lead.setdefault(lead, []).append(r)
    return r

for x in lsc:
    lead, t, typ = x["lead_id"], p(x["date_created"]), TYPE.get(x.get("new_status_label"))
    if not typ:
        continue
    last = (by_lead.get(lead) or [None])[-1]
    if last and t - p(last["start"]) < timedelta(days=21) and not last.get("_rebook_start"):
        # still the same lost call (status bounced, or re-entered while he was working it)
        mt = [m for m in meets if m["lead_id"] == lead and p(last["start"]) < p(m["date_created"]) < t and m.get("duration") == 2700]
        if not mt:
            continue
        last["_rebook_start"] = p(mt[0]["starts_at"])
    chain, no = (last["chain"], last["rebook_no"]) if last and last.get("_rebook_start") and t >= last["_rebook_start"] else (None, 0)
    found = "His 5:45 cancel" if (x.get("user_id") == GINO and typ == "Cancel") else ("Lead status" if x.get("user_id") != GINO else "Lead status (set by Gino)")
    new_row(lead, t, "Cancel (5:45)" if found == "His 5:45 cancel" else typ, found, chain, no)
for lead in sorted(field_leads - set(by_lead)):
    cs = [c for c in calls if c["lead_id"] == lead and c["user_id"] == GINO and c["direction"] == "outbound" and p(c["date_created"]).astimezone(ET).date() >= SCORE_FROM]
    st = info.get(lead, {}).get("status_label") or ""
    new_row(lead, p(cs[0]["date_created"]) if cs else et(SCORE_FROM, 0), (TYPE.get(st, "Backlog")) + " (backlog)", "Backlog (Call Recovery field)")

reviews, need_cal = [], []
cal_by_lead = {}
for c in cal:
    cal_by_lead.setdefault(c["lead_id"], []).append(c)

for lead, rs in by_lead.items():
    for i, r in enumerate(rs):
        start = p(r["start"])
        stop = p(rs[i + 1]["start"]) if i + 1 < len(rs) else now
        orig = [m for m in meets if m["lead_id"] == lead and m.get("duration") == 2700 and p(m["starts_at"]) <= start + timedelta(hours=24)
                and p(m["date_created"]) < start]
        if orig:
            o = orig[-1]
            r["orig_call"], r["advisor"] = p(o["starts_at"]).isoformat(), uname(o["user_id"])
        g = g_out(lead, start, stop)
        first = p(g[0]["date_created"]) if g else None
        r["first_attempt"] = first.isoformat() if first else None
        # reschedule request speed (during shift only)
        if r["type"] == "Reschedule request" and in_shift(start) and start.astimezone(ET).date() >= SCORE_FROM:
            mins = round((first - start).total_seconds() / 60) if first else None
            r["rr_minutes"], r["rr_on_time"] = mins, bool(first and mins <= 15)
        # rebook: the first closer-length meeting booked after the call was lost
        rb = [m for m in meets if m["lead_id"] == lead and m.get("duration") == 2700 and start < p(m["date_created"]) < stop]
        rbm = rb[0] if rb else None
        end_t, end_why = None, None
        if rbm:
            r["rebooked_at"], r["new_call"] = p(rbm["date_created"]).isoformat(), p(rbm["starts_at"]).isoformat()
            r["new_call_closer"] = uname(rbm["user_id"])
            end_t, end_why = p(rbm["date_created"]), "Rebooked"
            ce = [c for c in cal_by_lead.get(lead, []) if c.get("start") and p(c["start"]) == p(rbm["starts_at"])]
            if not ce and any(not c.get("event_uri") for c in cal_by_lead.get(lead, [])):
                r["calendar"], r["booked_by"] = "Not found in Calendly", "Unknown"
            elif ce:
                c = ce[0]
                r["calendar"] = "Closers round robin" if O2C in (c.get("event_type") or "") else (c.get("event_name") or "Other calendar")
                r["booked_by"] = "Gino" if c.get("scheduled_by") == GINO_CAL else ("Lead (public link)" if not c.get("scheduled_by") else "Someone else in Calendly")
                r["cal_status"] = c.get("status")
            else:
                r["calendar"], r["booked_by"] = "Not looked up yet", "Not looked up yet"
                need_cal.append(f"{lead}\t{email_of(lead)}\t{start.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            touched_before = bool(g_out(lead, start, end_t) or g_sms(lead, start, end_t))
            others = sorted({uname(c["user_id"]) for c in calls if c["lead_id"] == lead and c["user_id"] != GINO and c["direction"] == "outbound"
                             and (first or start) < p(c["date_created"]) < end_t})
            r["others_between"] = ", ".join(others)
            ok = touched_before and r["calendar"] == "Closers round robin" and r["booked_by"] == "Gino"
            r["credit"] = "Yes" if ok else ("Not looked up yet" if r["booked_by"] == "Not looked up yet" else "Check: not found in Calendly" if r["booked_by"] == "Unknown" else
                                         "No: " + ("he didn't touch the lead first" if not touched_before else
                                                   "not the round robin" if r["calendar"] != "Closers round robin" else
                                                   "lead booked it from the link" if r["booked_by"] == "Lead (public link)" else "someone else booked it"))
            # result of the new call
            cd = p(rbm["starts_at"])
            if r.get("cal_status") == "canceled" or rbm.get("status") == "canceled":
                res = "Cancelled or rescheduled"
            elif cd > now:
                res = "Upcoming"
            elif f"{cd.astimezone(ET).date().isoformat()}|{lead}" in eod:
                res = eod[f"{cd.astimezone(ET).date().isoformat()}|{lead}"][0]
            elif zoom(rbm):
                res = zoom(rbm)
            else:
                res = (prev.get(r["id"]) or {}).get("result") or "Unknown"
            r["result"] = res
            # logging: a Call Confirmation Specialist activity when he rebooks
            if r["booked_by"] == "Gino":
                a = [x for x in acts if x["lead_id"] == lead and start <= p(x["date_created"]) <= end_t + timedelta(days=1)]
                r["activity_logged"] = "Yes" if a else "No"
        elif (info.get(lead, {}).get(REC_CF) or "") == "Not Interested" and i == len(rs) - 1 and g:
            conn = [c for c in g if is_conn(c)]
            end_t, end_why = p((conn or g)[-1]["date_created"]), "Not interested"
        # the 5 days
        days = []
        if first:
            for k, d in enumerate(bdays(first.astimezone(ET).date(), 5), 1):
                if end_t and et(d, 0) > end_t:
                    days.append({"date": d.isoformat(), "day": k, "status": "not due", "what": end_why})
                    continue
                if d > TODAY:
                    days.append({"date": d.isoformat(), "day": k, "status": "ahead"})
                    continue
                if False:
                    days.append({"date": d.isoformat(), "day": k, "status": "not due", "what": end_why})
                    continue
                pz = paused(lead, d)
                if pz:
                    days.append({"date": d.isoformat(), "day": k, "status": "not due", "what": f"paused: callback task {pz.strftime('%b %-d')}"})
                    continue
                c = day_check(lead, d, k)
                if end_t and end_t.astimezone(ET).date() == d and not c["done"]:
                    c.update(done=True, what=end_why)
                key = f"rec|{r['id']}|day{k}"
                if not c["done"] and key in overrides:
                    c.update(done=True, what="Excused: " + overrides[key])
                c["status"] = "done" if c["done"] else ("not scored" if d < SCORE_FROM else "missed")
                # Call Recovery field for that day (only days covered by this run's field history)
                if c["status"] == "done" and d >= FEV_FROM and fev is not None and glob.glob(f"{D}/g_ev*.json"):
                    vals = [((e.get("data") or {}).get(REC_CF) or "") for e in fev if e.get("lead_id") == lead
                            and et(d, 0) <= p(e["date_updated"]) < et(d + timedelta(days=1), 2)]
                    ok = any(v.startswith(f"Day {k} ") or v in ("Rebooked", "Not Interested") for v in vals)
                    c["field"] = "Yes" if ok else ("Wrong: " + vals[-1] if vals else "Not set")
                elif (prev.get(r["id"]) or {}).get("days"):
                    old = next((x for x in prev[r["id"]]["days"] if x.get("date") == c["date"]), {})
                    if "field" in old:
                        c["field"] = old["field"]
                days.append(c)
            if not end_t and all(x["status"] in ("done", "missed", "not scored") for x in days) and len(days) == 5:
                end_why = "Sequence done"
        r["days"] = days
        r["status"] = (end_why if end_why else ("Waiting for first attempt" if not first else
                       f"Open (day {next((x['day'] for x in days if x['status'] == 'ahead'), 5)} of 5)"))
        if r["found_by"].startswith("Backlog") and not first:
            r["status"] = "Backlog: no call yet"
        r["field_now"] = info.get(lead, {}).get(REC_CF) or ""
        # bonus: once per chain
        r["bonus"] = 0
        if r.get("credit") == "Yes" and str(r.get("result", "")).startswith("Showed"):
            paid = [x for x in rows if x["chain"] == r["chain"] and x is not r and x.get("bonus")]
            if not paid:
                r["bonus"], r["show_date"] = BONUS, p(r["new_call"]).astimezone(ET).date().isoformat()
                sd = p(r["new_call"]).astimezone(ET).date()
                r["bonus_week"] = (sd - timedelta(days=sd.weekday())).isoformat()
        # reviews (coaching only)
        nm = r["lead_name"]
        for x in days:
            if x["status"] == "missed":
                reviews.append(dict(key=f"rec|{r['id']}|day{x['day']}", date=x["date"], lead_name=nm, lead_id=lead,
                                    section=f"Recovery · {r['type'].split(' (')[0].lower()} day {x['day']}", what=x["what"]))
            if x.get("field", "Yes") != "Yes" and x["status"] == "done":
                reviews.append(dict(key=f"rec|{r['id']}|field{x['day']}", date=x["date"], lead_name=nm, lead_id=lead,
                                    section="Recovery logging", what=f"Call Recovery field for day {x['day']}: {x['field']}"))
        if r.get("rr_on_time") is False:
            reviews.append(dict(key=f"rec|{r['id']}|rr15", date=start.astimezone(ET).date().isoformat(), lead_name=nm, lead_id=lead,
                                section="Recovery · reschedule request speed",
                                what=f"first call {r['rr_minutes']} min after the request" if r.get("rr_minutes") is not None else "not called"))
        if r.get("activity_logged") == "No":
            reviews.append(dict(key=f"rec|{r['id']}|activity", date=p(r["rebooked_at"]).astimezone(ET).date().isoformat(), lead_name=nm,
                                lead_id=lead, section="Recovery logging",
                                what=f"rebooked {fmt(p(r['rebooked_at']))} for {fmt(p(r['new_call']))}, no Call Confirmation Specialist activity"))
    for x in rs:
        x.pop("_rebook_start", None)

# activity logged with no rebook behind it
for a in acts:
    rs = by_lead.get(a["lead_id"], [])
    if not any(r.get("rebooked_at") and abs(p(r["rebooked_at"]) - p(a["date_created"])) <= timedelta(days=1) for r in rs) and p(a["date_created"]).astimezone(ET).date() >= SCORE_FROM:
        reviews.append(dict(key=f"rec|act|{a['id']}", date=p(a["date_created"]).astimezone(ET).date().isoformat(),
                            lead_name=info.get(a["lead_id"], {}).get("display_name") or a["lead_id"], lead_id=a["lead_id"],
                            section="Recovery logging", what="Call Confirmation Specialist activity logged, but no new booking found"))
reviews = [x for x in reviews if x["date"] >= SCORE_FROM.isoformat() and x["date"] <= TODAY.isoformat()]

# ---------------- per day ----------------
daily = {}
d = SCORE_FROM
while d <= TODAY:
    ds = d.isoformat()
    new = [r for r in rows if p(r["start"]).astimezone(ET).date() == d]
    cnt = lambda t: sum(1 for r in new if r["type"].startswith(t) and "backlog" not in r["type"])
    rr = [r for r in rows if "rr_on_time" in r and p(r["start"]).astimezone(ET).date() == d]
    dd = [(r, x) for r in rows for x in r["days"] if x["date"] == ds and x["status"] in ("done", "missed")]
    d1 = [x for r, x in dd if x["day"] == 1]
    d25 = [x for r, x in dd if x["day"] > 1]
    logerr = [x for x in reviews if x["date"] == ds and x["section"] == "Recovery logging"]
    open_ = [r for r in rows if p(r["start"]).astimezone(ET).date() <= d and r.get("first_attempt")
             and any(x["date"] == ds and x["status"] in ("done", "missed") for x in r["days"])]
    reached = [r for r, x in dd if x.get("what") == "reached"]
    rebooked = [r for r in rows if r.get("rebooked_at") and p(r["rebooked_at"]).astimezone(ET).date() == d and r.get("booked_by") == "Gino"]
    shows = [r for r in rows if r.get("show_date") == ds]
    daily[ds] = dict(new_ns=cnt("No-show"), new_cxl=cnt("Cancel"), new_rr=cnt("Reschedule"),
                     new_backlog=sum(1 for r in new if "backlog" in r["type"]),
                     rr_due=len(rr), rr_ok=sum(1 for r in rr if r["rr_on_time"]),
                     d1_due=len(d1), d1_ok=sum(1 for x in d1 if x["status"] == "done"),
                     d25_due=len(d25), d25_ok=sum(1 for x in d25 if x["status"] == "done"),
                     log_err=len(logerr), worked=len(open_), reached=len(reached), rebooked=len(rebooked),
                     shows=len(shows), shows_backlog=sum(1 for r in shows if "backlog" in r["type"]), bonus=sum(r["bonus"] for r in shows))
    d += timedelta(days=1)

json.dump(rows, open(f"{D}/rec_rows.json", "w"), indent=0, default=str)
json.dump(daily, open(f"{D}/rec_daily.json", "w"), indent=0)
json.dump(reviews, open(f"{D}/rec_reviews.json", "w"), indent=0)
open(f"{D}/need_rec_cal.txt", "w").write("\n".join(sorted(set(need_cal))) + ("\n" if need_cal else ""))
print(f"{len(rows)} recovery rows ({sum(1 for r in rows if 'backlog' in r['type'])} backlog), "
      f"{sum(1 for r in rows if r.get('rebooked_at'))} rebooked, {sum(1 for r in rows if r.get('credit') == 'Yes')} credited, "
      f"${sum(r['bonus'] for r in rows)} bonus; {len(reviews)} review items; {len(set(need_cal))} need a Calendly lookup (need_rec_cal.txt)")
