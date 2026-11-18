"""Offline: match Reviews items to approvals Sheila or Jay already gave in #cc-gino. No network.

usage: python3 -I slack_match.py DIR LIVE_XLSX

Reads DIR/calls_all.json, DIR/cc_gino_approvals.json (all approvals so far, from Supabase plus this run's scan) and
the Reviews tab of LIVE_XLSX. Writes:
  DIR/slack_decisions.json  {review_key: {decision, decided_by, decision_ts, summary, link}} for every item covered
  DIR/reviews_fill.json     GOOGLESHEETS_UPDATE_VALUES_BATCH data that fills H-J on EXISTING Reviews rows that a
                            Slack decision covers: rows whose H, I and J are all blank, or rows this run filled from
                            Slack earlier (J ends in "(Slack)") when the newest Slack decision now says otherwise.
                            A decision a person typed into the sheet is never touched.
reviews.py then pre-fills H-J on new rows from slack_decisions.json.

Matching (decisions with scope "this lead only"; the newest approved/denied decision that covers a call wins, and
"approved" -> H "Excused", "denied" -> H "Counts as a miss" (Sheila, Nov 18: she and Jay decide every scorecard item in
the thread; the run fills the Reviews tab so they don't have to)):
  the decision names the row's Close lead id, or the row's lead name (case and spacing ignored), AND it was given for
  that call: if it names a date, that date is the call's date, day-before date or booking date; if it names none, it
  was raised within 7 days before the call. If the decision lists `checkpoints` (welcome / daybefore / 545 / logging),
  it covers only those items for that lead (a scorecard reply names items by number).
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
# Lead-specific decisions, approved or denied: the newest one that covers a call wins (Nov 18: Sheila denied Atembeoh
# Anu's Nov 18 welcome call, which an older Nov 16 approval for the same lead would otherwise have excused).
decisions = sorted((a for a in load("cc_gino_approvals.json", [])
                    if a.get("decision") in ("approved", "denied") and a.get("scope") == "this lead only"),
                   key=lambda a: float(str(a.get("decision_ts") or a.get("raised_ts") or "0").split("#")[0]))
approvals = [a for a in decisions if a["decision"] == "approved"]


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
    cdm = (a.get("call_date_mentioned") or "")[:10]
    if cdm:   # a dated decision covers only that call: its call date, day-before date or booking date (Nov 18)
        return cdm in {call.isoformat(), str(r.get("db_date") or "")[:10], str(r.get("booked_date") or "")[:10]}
    return call - timedelta(days=7) <= raised <= call + timedelta(days=1)


def decide(key, kind):
    if kind not in KINDS:
        return None
    r = calls.get(key.split("|")[0])
    if not r:
        return None
    suffix = key.split("|")[1]
    for a in reversed(decisions):
        if not covers(a, r) or (a.get("checkpoints") and suffix not in a["checkpoints"]):
            continue
        if a["decision"] == "denied" and not a.get("checkpoints"):
            continue   # "counts as a miss" only fills the items it names; never a lead's other open items
        ts = a.get("decision_ts") or a.get("raised_ts")
        return {"decision": "Excused" if a["decision"] == "approved" else "Counts as a miss", "decided_by": f"{a.get('decided_by')} (Slack)", "decision_ts": ts,
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
        h, j = ws.cell(i, 8).value, str(ws.cell(i, 10).value or "")
        filled = any(ws.cell(i, c).value not in (None, "") for c in (8, 9, 10))
        if filled and not (j.endswith("(Slack)") and h != out[key]["decision"]):
            continue   # a person's decision, or already the same: leave it
        d = out[key]
        fill.append({"range": f"Reviews!H{i}:J{i}", "values": [[
            d["decision"], f"{'Approved' if d['decision'] == 'Excused' else 'Decided'} in #cc-gino: {d['summary']} {d['link']}".strip(), d["decided_by"]]]})

json.dump(out, open(os.path.join(DIR, "slack_decisions.json"), "w"), indent=1)
json.dump(fill, open(os.path.join(DIR, "reviews_fill.json"), "w"))
print(json.dumps({"approvals_lead_specific": len(approvals), "keys_covered": len(out), "existing_rows_to_fill": len(fill)}))
