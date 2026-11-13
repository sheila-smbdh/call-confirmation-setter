"""Offline: work out which day(s) this morning's scorecard covers and print the Supabase reads to run.

Usage: python3 -I scorecard/plan.py TODAY DIR      (TODAY = today's date in US Eastern, YYYY-MM-DD)

Prints one line per read: `<output file> <url>`. Run each as its own inline curl (see scorecard/ROUTINE.md):
    curl -s "<url>" -o <DIR>/<output file>
Also writes DIR/plan.json for build_card.py. No network.

Which days:
- Tuesday to Friday: the day before (the scored day).
- Monday: Friday is the scored day; Saturday and Sunday go in the "Weekend (not scored)" line.
- Saturday and Sunday: nothing is sent (prints SKIP).
"""
import json, os, sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BASE = "https://suoblmuvrmyfmuvlhqce.supabase.co/rest/v1"
GINO = "user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo"

today, d = date.fromisoformat(sys.argv[1]), sys.argv[2]
os.makedirs(d, exist_ok=True)
wd = today.weekday()  # Mon = 0
if wd >= 5:
    print("SKIP: no scorecard on weekends")
    sys.exit(0)
day = today - timedelta(days=3 if wd == 0 else 1)
weekend = [day + timedelta(days=1), day + timedelta(days=2)] if wd == 0 else []
last = weekend[-1] if weekend else day
utc = lambda x: datetime.combine(x, time(0), ET).astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

plan = {"today": today.isoformat(), "day": day.isoformat(), "weekend": [w.isoformat() for w in weekend]}
json.dump(plan, open(f"{d}/plan.json", "w"))

reads = [
    ("runs.json", f"{BASE}/call_confirm_runs?select=run_id,today,data_through,status&status=eq.ok&order=run_id.desc&limit=1"),
    ("daily.json", f"{BASE}/call_confirm_daily?select=day,row&day=gte.{day}&day=lte.{last}"),
    ("reviews.json", f"{BASE}/call_confirm_reviews?select=day,checkpoint,kind,lead_name,what_happened,note,decision"
                     f"&day=eq.{day}&order=checkpoint,lead_name"),
    ("dials.json", f"{BASE}/call_confirm_raw_records?select=occurred_at&source=eq.close_call"
                   f"&payload->>user_id=eq.{GINO}&payload->>direction=eq.outbound"
                   f"&occurred_at=gte.{utc(day)}&occurred_at=lt.{utc(last + timedelta(days=1))}&order=occurred_at"),
]
for f, u in reads:
    print(f, u)
