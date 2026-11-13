"""Offline: merge this run's rebuilt calls with the rows already in the tracker. No network.

Usage: python3 -I merge.py DATA_DIR TRACKER_XLSX
  TRACKER_XLSX: the live tracker exported as .xlsx (Google Drive download_file_content).
  Reads the hidden "Row data" column on the Calls tab, replaces any call rebuilt this run (DATA_DIR/calls_new.json),
  adds new ones, and writes DATA_DIR/calls_all.json. Also writes DATA_DIR/review_keys.json (keys already on Reviews)
  and DATA_DIR/reviews_last_row.txt.
"""
import json, sys
from openpyxl import load_workbook

D, X = sys.argv[1], sys.argv[2]
wb = load_workbook(X, read_only=True)
old = {}
ws = wb["Calls"]
hdr = [c.value for c in next(ws.iter_rows(min_row=2, max_row=2))]
jc = next((i for i, h in enumerate(hdr) if h and str(h).startswith("Row data")), None)
if jc is None:
    print("No row-data column on Calls yet (first run): starting from this run's rows only")
else:
    for row in ws.iter_rows(min_row=3, values_only=True):
        if jc < len(row) and row[jc]:
            r = json.loads(row[jc])
            old[r["event"]] = r
new = json.load(open(f"{D}/calls_new.json"))
merged = dict(old)
GENERIC = "Logging error: invite not accepted when he logged it (check the call transcript)"
for r in new:
    o = old.get(r["event"])
    # Keep a logging judgment made earlier from the call transcript (e.g. "Valid (verbal + tech issue): ...")
    if o and r.get("check", "").startswith(GENERIC) and o.get("check") and not o["check"].startswith(GENERIC):
        r["check"] = o["check"]
    merged[r["event"]] = r
json.dump(list(merged.values()), open(f"{D}/calls_all.json", "w"), default=str)
print(f"{len(old)} rows from the tracker, {len(new)} rebuilt this run, {len(merged)} total")

rv = wb["Reviews"]
rhdr = [c.value for c in next(rv.iter_rows(min_row=1, max_row=1))]
kc = next((i for i, h in enumerate(rhdr) if h and str(h).startswith("Key")), None)
keys, last = [], 1
for i, row in enumerate(rv.iter_rows(min_row=2, values_only=True), 2):
    if row and row[0] not in (None, ""):
        last = i
        if kc is not None and kc < len(row) and row[kc]:
            keys.append(row[kc])
json.dump(keys, open(f"{D}/review_keys.json", "w"))
open(f"{D}/reviews_last_row.txt", "w").write(str(last))
print(len(keys), "review keys already on the tracker; last Reviews row", last)
