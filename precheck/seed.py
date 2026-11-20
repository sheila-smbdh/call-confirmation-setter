"""Offline: turn this morning's saved records (Supabase reads from precheck/ROUTINE.md step 1) into the files
tracker/pipeline/build.py reads, so the pre-check only looks up what changed since the morning run. No network.

Usage: python3 -I precheck/seed.py DIR
Reads (each optional; a missing or non-list file counts as empty):
  prev_invitees.json  [{"payload": <cal_invitees.jsonl line>}]           -> cal_invitees.jsonl
  prev_alerts.json    [{"payload": <slack_alerts.jsonl line>}]           -> slack_alerts.jsonl
  prev_overrides.json [{"record_id": lead, "payload": {"judgment": ...}}] -> overrides.json
  prev_lead_fix.json  [{"record_id": event_uri, "payload": {"lead_id"}}] -> lead_fix.json
  prev_text.json      [{"record_id": lead, "payload": {"at", "text"}}]   -> text_confirms.json
Also writes an empty eod_recent.json (show results don't matter to the pre-check).
"""
import json, os, sys

D = sys.argv[1]


def rows(name):
    try:
        x = json.load(open(f"{D}/{name}"))
    except (FileNotFoundError, ValueError):
        return []
    return x if isinstance(x, list) else []


def jsonl(name, recs, key):
    seen, out = set(), []
    for r in recs:
        if isinstance(r, dict) and r.get(key) not in seen:
            seen.add(r.get(key))
            out.append(json.dumps(r))
    open(f"{D}/{name}", "w").write("\n".join(out) + ("\n" if out else ""))
    return len(out)


n_inv = jsonl("cal_invitees.jsonl", [x["payload"] for x in rows("prev_invitees.json")], "event_uri")
n_al = jsonl("slack_alerts.jsonl", [x["payload"] for x in rows("prev_alerts.json")], "ts")
ov = {x["record_id"]: x["payload"]["judgment"] for x in rows("prev_overrides.json") if x.get("payload", {}).get("judgment")}
lf = {x["record_id"]: x["payload"]["lead_id"] for x in rows("prev_lead_fix.json") if x.get("payload", {}).get("lead_id")}
tc = {x["record_id"]: {"at": x["payload"]["at"], "text": x["payload"].get("text", "")}
      for x in rows("prev_text.json") if x.get("payload", {}).get("at")}
json.dump(ov, open(f"{D}/overrides.json", "w"))
json.dump(lf, open(f"{D}/lead_fix.json", "w"))
json.dump(tc, open(f"{D}/text_confirms.json", "w"))
json.dump({}, open(f"{D}/eod_recent.json", "w"))
print(f"seeded: {n_inv} invitee events, {n_al} alerts, {len(ov)} overrides, {len(lf)} lead fixes, {len(tc)} text confirms")
