"""Offline: new rows for the Reviews tab (misses and logging errors that need Sheila's or Jay's call). No network.

Usage: python3 -I reviews.py DATA_DIR
  Reads calls_all.json, review_keys.json, reviews_last_row.txt. Writes DATA_DIR/reviews_append.json: the "data" list
  for GOOGLESHEETS_UPDATE_VALUES_BATCH (valueInputOption USER_ENTERED). Columns A-G get the facts, H-J stay blank for
  the decision, K is a formula that fills itself, L is the key. Existing rows and decisions are never touched.
"""
import json, sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

D = sys.argv[1]
ET = ZoneInfo("America/New_York")
rows = json.load(open(f"{D}/calls_all.json"))
have = set(json.load(open(f"{D}/review_keys.json")))
last = int(open(f"{D}/reviews_last_row.txt").read().strip())
dt = lambda s: datetime.fromisoformat(s).astimezone(ET)
wk = lambda d: d - timedelta(days=d.weekday())

def items():
    out = []
    def add(dstr, cp, kind, r, what, note, key):
        d = date.fromisoformat(dstr)
        out.append((wk(d), d, cp, kind, r["lead_name"], what, note, key))
    for r in rows:
        w, b = r.get("w"), r.get("db")
        if r.get("w_required") == "Yes" and w and not w["finished"] and r.get("w_due"):
            due = dt(r["w_due"])
            cp = "Welcome call (during shift)" if r["booking_type"] == "During shift" else "Welcome call (overnight)"
            note = "Booked in the last 15 minutes of his shift" if r["booking_type"] == "During shift" and due.hour == 20 else ""
            add(due.date().isoformat(), cp, "Miss", r, w["dropoff"] + f" (booked {r['booked_date'][5:]} {r['booked_et']}, call {r['call_date'][5:]} {r['call_et']})", note, f"{r['event']}|welcome")
        if r.get("db_counts") == "Yes" and b and not b["finished"]:
            add(r["db_date"], "Day-before call", "Miss", r, b["dropoff"] + f" (call {r['call_date'][5:]} {r['call_et']})",
                "Out of his view because of his own logging error" if "logged it accepted when it wasn't" in r.get("db_reason", "") else "", f"{r['event']}|daybefore")
        if r.get("r_counts") == "Yes" and r.get("r_result") != "Cancelled":
            add(r["db_date"], "5:45 cancel", "Miss", r, f"{r.get('r_result')} (call {r['call_date'][5:]} {r['call_et']})",
                "Booked that same day" if r["booked_date"] == r["db_date"] else "", f"{r['event']}|545")
        if r.get("check", "").startswith("Logging error"):
            add(r["booked_date"], "Logging", "Logging error", r, r["check"].replace("Logging error: ", ""),
                "Judge: edge case he couldn't have known, or a real miss?", f"{r['event']}|logging")
    return sorted(out, key=lambda x: (x[0], x[1], x[2], x[4]))

data, n = [], last
for it in items():
    if it[7] in have:
        continue
    n += 1
    data.append({"range": f"Reviews!A{n}:G{n}", "values": [[it[0].isoformat(), it[1].isoformat(), it[2], it[3], it[4], it[5], it[6]]]})
    data.append({"range": f"Reviews!L{n}", "values": [[it[7]]]})
json.dump(data, open(f"{D}/reviews_append.json", "w"))
print(len(data) // 2, "new Reviews rows", f"(rows {last + 1}-{n})" if data else "")
