"""Stage one run's data for Supabase (setter-data). Offline: reads local files, writes upload files. Never calls Supabase.

usage: python3 -I supa.py DIR RUN_ID POST_RUN_XLSX

DIR            the run folder (tracker/data/<TODAY>)
RUN_ID         e.g. 2026-11-13T20:00-07:00
POST_RUN_XLSX  the tracker exported AFTER this run's writes (values, not formulas); "-" = raw records only (backfill)

Writes DIR/supa/NN_<table>.json (JSON arrays, at most 500 rows each) and DIR/supa/manifest.tsv with one line per file:
<table>\t<on_conflict columns>\t<file>. The runbook uploads each file with one inline curl (upsert).
"""
import glob
import json
import os
import sys
from datetime import date, datetime, timezone

import openpyxl

DIR, RUN_ID, XLSX = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = os.path.join(DIR, "supa")
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*")):
    os.remove(f)
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
manifest = []


def jval(v):
    if isinstance(v, datetime):
        return v.date().isoformat() if (v.hour, v.minute, v.second) == (0, 0, 0) else v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return v


def emit(table, conflict, rows):
    if not rows:
        return
    # one primary key per file, or the upsert fails
    seen, uniq = set(), []
    keys = conflict.split(",")
    for r in reversed(rows):
        k = tuple(r.get(c) for c in keys)
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    uniq.reverse()
    for i in range(0, len(uniq), 500):
        fn = os.path.join(OUT, f"{len(manifest):02d}_{table}.json")
        with open(fn, "w") as fh:
            json.dump(uniq[i:i + 500], fh, default=str)
        manifest.append((table, conflict, fn))


def load(path):
    with open(path) as fh:
        return json.load(fh)


def jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


# ---------------- raw records ----------------
raw = []


def add(source, rid, payload, lead_id=None, at=None):
    if rid is None:
        return
    raw.append({"source": source, "record_id": str(rid), "lead_id": lead_id, "occurred_at": at,
                "payload": payload, "last_run_id": RUN_ID, "last_seen_at": NOW})


def close_files(pattern, source, at_field):
    for f in sorted(glob.glob(os.path.join(DIR, pattern))):
        d = load(f)
        for r in d.get("data", []) if isinstance(d, dict) else []:
            add(source, r.get("id"), r, r.get("lead_id"), r.get(at_field))


close_files("g_call_*.json", "close_call", "date_created")
close_files("g_sms_*.json", "close_sms", "date_created")
close_files("g_ev_*.json", "close_event", "date_created")
close_files("ev_*.json", "close_event", "date_created")
for f in sorted(glob.glob(os.path.join(DIR, "act_*.json"))):
    d = load(f)
    for r in d.get("data", []) if isinstance(d, dict) else []:
        add("close_" + str(r.get("_type", "activity")).lower(), r.get("id"), r, r.get("lead_id"), r.get("date_created"))
close_files("meet_*.json", "close_meeting", "starts_at")
close_files("lsc_*.json", "close_status_change", "date_created")
close_files("acc_*.json", "close_calendar_response", "date_created")
for f in sorted(glob.glob(os.path.join(DIR, "tr_*.json"))):
    r = load(f)
    add("close_call_transcript", r.get("id"), r)
for r in jsonl(os.path.join(DIR, "cal_events.jsonl")):
    add("calendly_event", r.get("uri"), r, None, r.get("start"))
for r in jsonl(os.path.join(DIR, "cal_invitees.jsonl")):
    add("calendly_invitee", f"{r.get('event_uri')}|{r.get('email')}", r, None, r.get("created_at"))
for r in jsonl(os.path.join(DIR, "slack_alerts.jsonl")):
    add("slack_call_confirmation", r.get("ts"), r, r.get("lead_id"))
for f in ("eod_recent.json",):
    p = os.path.join(DIR, f)
    if os.path.exists(p):
        for k, v in load(p).items():
            day, lead = k.split("|", 1)
            add("slack_closer_eod", k, {"day": day, "lead_id": lead, "result": v[0], "closer": v[1]}, lead, day)
for r in jsonl(os.path.join(DIR, "cc_gino_messages.jsonl")):
    add("slack_cc_gino", r.get("ts"), r)
for f in sorted(glob.glob(os.path.join(DIR, "sms_lead_*.json"))):
    d = load(f)
    for r in d.get("data", []) if isinstance(d, dict) else []:
        add("close_sms", r.get("id"), r, r.get("lead_id"), r.get("date_created"))
p = os.path.join(DIR, "text_confirms.json")
if os.path.exists(p):
    for k, v in load(p).items():
        add("text_confirmation", k, dict(v, lead_id=k), k, v.get("at"))
p = os.path.join(DIR, "overrides.json")
if os.path.exists(p):
    for k, v in load(p).items():
        add("judgment_override", k, {"lead_id": k, "judgment": v}, k)
p = os.path.join(DIR, "lead_fix.json")
if os.path.exists(p):
    for k, v in load(p).items():
        add("lead_fix", k, {"event_uri": k, "lead_id": v}, v)
emit("call_confirm_raw_records", "source,record_id", raw)

# ---------------- calls (from the pipeline's merged rows) ----------------
calls = []
for r in (load(os.path.join(DIR, "calls_all.json")) if os.path.exists(os.path.join(DIR, "calls_all.json")) else []):
    calls.append({"event_uri": r["event"], "lead_id": r.get("lead_id"), "lead_name": r.get("lead_name"),
                  "email": r.get("email"), "closer": r.get("closer"), "call_date": r.get("call_date"),
                  "call_et": r.get("call_et"), "booked_date": r.get("booked_date"), "booked_et": r.get("booked_et"),
                  "booking_type": r.get("booking_type"), "logging_check": r.get("check"),
                  "happened": r.get("happened"), "row": r, "last_run_id": RUN_ID, "updated_at": NOW})
emit("call_confirm_calls", "event_uri", calls)

# ---------------- sheet values after the run ----------------
wb = openpyxl.load_workbook(XLSX, data_only=True) if XLSX != "-" else openpyxl.Workbook()
snaps = []
for ws in (wb.worksheets if XLSX != "-" else []):
    if ws.sheet_state != "visible":
        continue
    vals = [[jval(c) for c in row] for row in ws.iter_rows(values_only=True)]
    while vals and all(v in (None, "") for v in vals[-1]):
        vals.pop()
    snaps.append({"run_id": RUN_ID, "tab": ws.title, "rows": vals})
emit("call_confirm_tab_snapshots", "run_id,tab", snaps)


def headers(ws, rows):
    hs, group = [], None
    for j in range(1, ws.max_column + 1):
        parts = []
        for r in rows:
            v = ws.cell(r, j).value
            if r == rows[0] and len(rows) > 1:
                group = v if v not in (None, "") else group
                continue
            parts.append(v)
        name = " / ".join(str(p) for p in [group if len(rows) > 1 else None] + parts if p not in (None, ""))
        hs.append(name or f"col{j}")
    return hs


def table_rows(ws, hdr_rows, first, key_col=1):
    hs = headers(ws, hdr_rows)
    out = []
    for r in range(first, ws.max_row + 1):
        k = ws.cell(r, key_col).value
        if not isinstance(k, (datetime, date)):
            continue
        out.append((jval(k), {h: jval(ws.cell(r, j + 1).value) for j, h in enumerate(hs)}))
    return out


if "Daily" in wb.sheetnames:
    emit("call_confirm_daily", "day", [{"day": k, "row": v, "last_run_id": RUN_ID, "updated_at": NOW}
                             for k, v in table_rows(wb["Daily"], [1, 2], 3)])
if "Weekly" in wb.sheetnames:
    emit("call_confirm_weekly", "week_start", [{"week_start": k, "row": v, "last_run_id": RUN_ID, "updated_at": NOW}
                                     for k, v in table_rows(wb["Weekly"], [1], 2)])
if "Management" in wb.sheetnames:
    ws = wb["Management"]
    hr = next((r for r in range(1, 40) if ws.cell(r, 1).value == "Week starting (Mon)"), None)
    if hr:
        emit("call_confirm_management_weeks", "week_start",
             [{"week_start": k, "row": v, "last_run_id": RUN_ID, "updated_at": NOW}
              for k, v in table_rows(ws, [hr - 1, hr], hr + 1)])
if "Reviews" in wb.sheetnames:
    ws = wb["Reviews"]
    slack = {}
    p = os.path.join(DIR, "slack_decisions.json")
    if os.path.exists(p):
        slack = load(p)
    rv = []
    for r in range(2, ws.max_row + 1):
        key = ws.cell(r, 12).value
        if not key:
            continue
        v = [jval(ws.cell(r, j).value) for j in range(1, 11)]
        rv.append({"review_key": key, "sheet_row": r, "week_start": v[0], "day": v[1], "checkpoint": v[2],
                   "kind": v[3], "lead_name": v[4], "what_happened": v[5], "note": v[6], "decision": v[7],
                   "reason": v[8], "decided_by": v[9],
                   "decided_via": "slack" if key in slack else ("sheet" if v[7] else None),
                   "slack_ts": (slack.get(key) or {}).get("decision_ts"),
                   "last_run_id": RUN_ID, "updated_at": NOW})
    emit("call_confirm_reviews", "review_key", rv)

# ---------------- Slack approvals ----------------
from zoneinfo import ZoneInfo


def et_iso(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York")).isoformat()


p = os.path.join(DIR, "cc_gino_approvals.json")
if os.path.exists(p):
    ap = []
    for a in load(p):
        ap.append({"raised_ts": a["raised_ts"], "thread_ts": a.get("thread_ts"), "raised_by": a.get("raised_by"),
                   "raised_at": et_iso(a.get("raised_at_et")), "lead_ids": a.get("lead_ids") or [],
                   "lead_names": a.get("lead_names") or [], "call_date_mentioned": a.get("call_date_mentioned"),
                   "asked": a.get("what_gino_asked_or_reported"), "decision": a.get("decision"),
                   "decided_by": a.get("decided_by"), "decision_ts": a.get("decision_ts"), "scope": a.get("scope"),
                   "decision_summary": a.get("decision_summary"), "last_run_id": RUN_ID, "updated_at": NOW})
    emit("call_confirm_slack_approvals", "raised_ts", ap)

with open(os.path.join(OUT, "manifest.tsv"), "w") as fh:
    for t, c, f in manifest:
        fh.write(f"{t}\t{c}\t{f}\n")
counts = {}
for t, c, f in manifest:
    with open(f) as fh:
        counts[t] = counts.get(t, 0) + len(json.load(fh))
print(json.dumps({"files": len(manifest), "rows": counts}))
