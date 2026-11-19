"""Offline: new rows for the Reviews tab (misses and logging errors that need Sheila's or Jay's call). No network.

Usage: python3 -I reviews.py DATA_DIR
  Reads calls_all.json, review_keys.json, reviews_last_row.txt. Writes DATA_DIR/reviews_append.json: the "data" list
  for GOOGLESHEETS_UPDATE_VALUES_BATCH (valueInputOption USER_ENTERED). Columns A-G get the facts, H-J stay blank for
  the decision (unless Sheila or Jay already decided it in #cc-gino: then H-J say so), K is a formula that fills itself, L is the key. Existing rows and decisions are never touched.
"""
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

D = sys.argv[1]
ET = ZoneInfo("America/New_York")
rows = json.load(open(f"{D}/calls_all.json"))
have = set(json.load(open(f"{D}/review_keys.json")))
last = int(open(f"{D}/reviews_last_row.txt").read().strip())
try:
    slack = json.load(open(f"{D}/slack_decisions.json"))   # from slack_match.py; optional
except FileNotFoundError:
    slack = {}
try:
    hints = json.load(open(f"{D}/rule_hints.json"))       # {review_key: "Possibly covered by ... <link>"}; optional
except FileNotFoundError:
    hints = {}
# Gino's lead notes pulled in step 7c (note_lead_<lead_id>.json), shown on each Reviews row with his call notes
import glob, os
lead_notes = {}
for f in glob.glob(f"{D}/note_lead_*.json"):
    for n in json.load(open(f)).get("data", []):
        if "gino" in (n.get("user_name") or "").lower() and (n.get("note") or "").strip():
            lead_notes.setdefault(n["lead_id"], []).append((n["date_created"], " ".join(n["note"].split())[:150]))

def gino_notes(r, cp):
    parts = [x for x in ((cp or {}).get("notes") or "").split("; ") if x]
    parts += [t for _, t in sorted(lead_notes.get(r.get("lead_id"), []))[-2:] if t not in parts]
    return ("Gino's notes: " + " | ".join(parts)) if parts else ""

dt = lambda s: datetime.fromisoformat(s).astimezone(ET)
wk = lambda d: d - timedelta(days=d.weekday())

def items():
    out = []
    def add(dstr, cp, kind, r, what, note, key, chk=None):
        d = date.fromisoformat(dstr)
        note = "; ".join(x for x in (note, gino_notes(r, chk)) if x)
        out.append((wk(d), d, cp, kind, r["lead_name"], what, note, key))
    for r in rows:
        w, b = r.get("w"), r.get("db")
        if r.get("w_required") == "Yes" and w and not w["finished"] and r.get("w_due"):
            due = dt(r["w_due"])
            cp = "Welcome call (during shift)" if r["booking_type"] == "During shift" else "Welcome call (overnight)"
            note = "Booked in the last 15 minutes of his shift" if r["booking_type"] == "During shift" and due.hour == 20 else ""
            add(due.date().isoformat(), cp, "Miss", r, w["dropoff"] + f" (booked {r['booked_date'][5:]} {r['booked_et']}, call {r['call_date'][5:]} {r['call_et']})", note, f"{r['event']}|welcome", w)
        if r.get("db_counts") == "Yes" and b and not b["finished"]:
            add(r["db_date"], "Day-before call", "Miss", r, b["dropoff"] + f" (call {r['call_date'][5:]} {r['call_et']})",
                "Out of his view because of his own logging error" if "logged it accepted when it wasn't" in r.get("db_reason", "") else "", f"{r['event']}|daybefore", b)
        for f in r.get("fu") or []:   # Nov 19: daily follow-up calls, one item per day missed
            c = f.get("cp")
            if f.get("counts") == "Yes" and c and not c["finished"]:
                add(f["date"], "Follow-up call", "Miss", r, c["dropoff"] + f" (call {r['call_date'][5:]} {r['call_et']})", "",
                    f"{r['event']}|followup-{f['date']}", c)
        if r.get("r_counts") == "Yes" and r.get("r_result") != "Cancelled":
            add(r["db_date"], "5:45 cancel", "Miss", r, f"{r.get('r_result')} (call {r['call_date'][5:]} {r['call_et']})",
                "Booked that same day" if r["booked_date"] == r["db_date"] else "", f"{r['event']}|545", b)
        if r.get("check", "").startswith("Logging error"):
            add(r["booked_date"], "Logging", "Logging error", r, r["check"].replace("Logging error: ", ""),
                "Judge: edge case he couldn't have known, or a real miss?", f"{r['event']}|logging")
    return sorted(out, key=lambda x: (x[0], x[1], x[2], x[4]))

data, n = [], last
for it in items():
    if it[7] in have:
        continue
    n += 1
    note = "; ".join(x for x in (it[6], hints.get(it[7], "")) if x)
    data.append({"range": f"Reviews!A{n}:G{n}", "values": [[it[0].isoformat(), it[1].isoformat(), it[2], it[3], it[4], it[5], note]]})
    data.append({"range": f"Reviews!L{n}", "values": [[it[7]]]})
    d = slack.get(it[7])
    if d:   # Sheila or Jay already approved this in #cc-gino: record it so it doesn't wait for review
        data.append({"range": f"Reviews!H{n}:J{n}", "values": [[d["decision"],
                     f"{'Approved' if d['decision'] == 'Excused' else 'Decided'} in #cc-gino: {d['summary']} {d['link']}".strip(), d["decided_by"]]]})
json.dump(data, open(f"{D}/reviews_append.json", "w"))
new = n - last
pre = sum(1 for x in data if ":J" in x["range"])
print(new, "new Reviews rows", f"(rows {last + 1}-{n})" if new else "", f"{pre} already decided via Slack")
