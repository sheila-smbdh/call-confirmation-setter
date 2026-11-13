"""Offline: match Reviews items to approvals Sheila or Jay already gave in #cc-gino. No network.

usage: python3 -I slack_match.py DIR LIVE_XLSX

Reads DIR/calls_all.json, DIR/cc_gino_approvals.json (all approvals so far, from Supabase plus this run's scan) and
the Reviews tab of LIVE_XLSX. Writes:
  DIR/slack_decisions.json  {review_key: {decision, decided_by, decision_ts, summary, link}} for every item covered
  DIR/reviews_fill.json     GOOGLESHEETS_UPDATE_VALUES_BATCH data that fills H-J on EXISTING Reviews rows whose
                            H, I and J are all blank and that a Slack approval covers (never overwrites a decision)
reviews.py then pre-fills H-J on new rows from slack_decisions.json.

Matching (only approvals with decision "approved" and scope "this lead only"):
  the approval names the row's Close lead id, or the row's lead name (case and spacing ignored), AND the approval was
  given for that call: its call date matches, or it was raised within 7 days before the call.
Which review kinds a Slack approval can clear: see KINDS.
"""
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

import openpyxl

DIR, XLSX = sys.argv[1], sys.argv[2]
CHANNEL = "C0CG28G7TQT"
KINDS = {"Logging error", "Miss"}  # Sheila, Nov 13: a lead-specific approval clears that lead's misses and logging errors
norm = lambda s: re.sub(r"[^a-z]", "", (s or "").lower())


def load(p, default):
    p = os.path.join(DIR, p)
    return json.load(open(p)) if os.path.exists(p) else default


calls = {r["event"]: r for r in load("calls_all.json", [])}
approvals = [a for a in load("cc_gino_approvals.json", [])
             if a.get("decision") == "approved" and a.get("scope") == "this lead only"]


def link(ts):
    return f"https://dylanhelen.slack.com/archives/{CHANNEL}/p{str(ts).replace('.', '')}" if ts else ""


def covers(a, r):
    ids = set(a.get("lead_ids") or [])
    names = {norm(n) for n in a.get("lead_names") or []}
    if not (r.get("lead_id") in ids or norm(r.get("lead_name")) in names):
        return False
    try:
        call = date.fromisoformat(r["call_date"])
        raised = datetime.strptime(a["raised_at_et"], "%Y-%m-%d %H:%M").date()
    except (KeyError, TypeError, ValueError):
        return False
    cdm = a.get("call_date_mentioned") or ""
    if cdm[:10] == call.isoformat():
        return True
    return call - timedelta(days=7) <= raised <= call + timedelta(days=1)


def decide(key, kind):
    if kind not in KINDS:
        return None
    r = calls.get(key.split("|")[0])
    if not r:
        return None
    for a in approvals:
        if covers(a, r):
            ts = a.get("decision_ts") or a.get("raised_ts")
            return {"decision": "Excused", "decided_by": f"{a.get('decided_by')} (Slack)", "decision_ts": ts,
                    "summary": a.get("decision_summary") or "", "link": link(a.get("thread_ts") or a.get("raised_ts"))}
    return None


# every possible key for every call, so reviews.py can look up new rows
out = {}
for ev, r in calls.items():
    for suffix, kind in (("welcome", "Miss"), ("daybefore", "Miss"), ("545", "Miss"), ("logging", "Logging error")):
        d = decide(f"{ev}|{suffix}", kind)
        if d:
            out[f"{ev}|{suffix}"] = d

fill = []
wb = openpyxl.load_workbook(XLSX, data_only=True)
if "Reviews" in wb.sheetnames:
    ws = wb["Reviews"]
    for i in range(2, ws.max_row + 1):
        key, kind = ws.cell(i, 12).value, ws.cell(i, 4).value
        if not key or key not in out or kind not in KINDS:
            continue
        if any(ws.cell(i, j).value not in (None, "") for j in (8, 9, 10)):
            continue
        d = out[key]
        fill.append({"range": f"Reviews!H{i}:J{i}", "values": [[
            "Excused", f"Approved in #cc-gino: {d['summary']} {d['link']}".strip(), d["decided_by"]]]})

json.dump(out, open(os.path.join(DIR, "slack_decisions.json"), "w"), indent=1)
json.dump(fill, open(os.path.join(DIR, "reviews_fill.json"), "w"))
print(json.dumps({"approvals_lead_specific": len(approvals), "keys_covered": len(out), "existing_rows_to_fill": len(fill)}))
