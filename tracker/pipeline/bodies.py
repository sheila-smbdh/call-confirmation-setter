"""Offline: write the Close search request bodies for one nightly run. No network.

Usage:
  python3 -I bodies.py meetings DATA_DIR TODAY   -> DATA_DIR/body_meet_created.json, body_meet_starts.json
  python3 -I bodies.py leads DATA_DIR TODAY      -> DATA_DIR/body_lsc.json, body_acc.json (needs DATA_DIR/scope.json)
  python3 -I bodies.py split BODY_FILE           -> halves the body's date window into BODY_a.json / BODY_b.json
  python3 -I bodies.py check RESULT_FILE         -> OK, or TRUNCATED (then split the matching body and re-run both halves)

Every body is sent with one inline curl:  curl -s -u "$CLOSE_API_KEY:" -X POST "https://api.close.com/api/v1/data/search/" \
  -H "Content-Type: application/json" -d @BODY -o RESULT
"""
import json, sys, os
from datetime import date, datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
utc = lambda d: datetime.combine(d, time(0, 0), ET).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def rng(ot, field, lo, hi):
    return {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": field},
            "condition": {"type": "moment_range", "on_or_after": {"type": "fixed_utc", "value": lo}, "before": {"type": "fixed_utc", "value": hi}}}

def meet(field, lo, hi):
    ot = "activity.meeting"
    return {"query": {"type": "and", "queries": [{"type": "object_type", "object_type": ot}, rng(ot, field, lo, hi),
            {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "duration"},
             "condition": {"type": "number_range", "gte": 2700, "lte": 2700}}]},
            "_fields": {ot: ["id", "lead_id", "user_id", "starts_at", "ends_at", "status", "title", "date_created", "attendees", "integrations", "duration"]},
            "_limit": 200, "include_counts": True}

def leads_q(ot, lo, hi, leads, extra=None, fields=None):
    q = [{"type": "object_type", "object_type": ot}, rng(ot, "date_created", lo, hi),
         {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "lead_id"},
          "condition": {"type": "reference", "reference_type": "lead", "object_ids": sorted(leads)}}]
    if extra:
        q.append(extra)
    return {"query": {"type": "and", "queries": q}, "_fields": {ot: fields}, "_limit": 200, "include_counts": True}

def main():
    mode = sys.argv[1]
    if mode in ("meetings", "leads"):
        D, today = sys.argv[2], date.fromisoformat(sys.argv[3])
    if mode == "meetings":
        json.dump(meet("date_created", utc(today - timedelta(days=4)), NOW), open(f"{D}/body_meet_created.json", "w"))
        json.dump(meet("starts_at", utc(today - timedelta(days=3)), utc(today + timedelta(days=5))), open(f"{D}/body_meet_starts.json", "w"))
        print("wrote body_meet_created.json, body_meet_starts.json")
    elif mode == "leads":
        scope = json.load(open(f"{D}/scope.json"))
        leads = {c[1] for e in scope for c in e["close"]} | set(json.load(open(f"{D}/lead_fix.json")).values() if os.path.exists(f"{D}/lead_fix.json") else [])
        for l in open(f"{D}/slack_alerts.jsonl") if os.path.exists(f"{D}/slack_alerts.jsonl") else []:
            x = json.loads(l)
            if x.get("lead_id"):
                leads.add(x["lead_id"])
        lo = utc(today - timedelta(days=30))
        json.dump(leads_q("activity.lead_status_change", lo, NOW, leads, fields=["id", "lead_id", "user_id", "date_created", "old_status_label", "new_status_label"]),
                  open(f"{D}/body_lsc.json", "w"))
        ot = "activity.email"
        subj = lambda w: {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "subject"},
                          "condition": {"type": "text", "mode": "beginning_of_words", "value": w}}
        extra = {"type": "and", "queries": [
            {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "direction"}, "condition": {"type": "term", "values": ["incoming"]}},
            {"type": "or", "queries": [subj("Accepted"), subj("Declined")]}]}
        json.dump(leads_q(ot, lo, NOW, leads, extra, ["id", "lead_id", "date_created", "subject", "sender"]), open(f"{D}/body_acc.json", "w"))
        print(len(leads), "leads; wrote body_lsc.json, body_acc.json")
    elif mode == "split":
        f = sys.argv[2]
        b = json.load(open(f))
        c = next(q for q in b["query"]["queries"] if q.get("type") == "field_condition" and q["condition"].get("type") == "moment_range")["condition"]
        lo = datetime.fromisoformat(c["on_or_after"]["value"].replace("Z", "+00:00"))
        hi = datetime.fromisoformat(c["before"]["value"].replace("Z", "+00:00"))
        mid = (lo + (hi - lo) / 2).strftime("%Y-%m-%dT%H:%M:%SZ")
        stem = f[:-5]
        c["before"]["value"] = mid
        json.dump(b, open(stem + "_a.json", "w"))
        c["before"]["value"], c["on_or_after"]["value"] = hi.strftime("%Y-%m-%dT%H:%M:%SZ"), mid
        json.dump(b, open(stem + "_b.json", "w"))
        os.remove(f)
        print("split into", stem + "_a.json", stem + "_b.json")
    elif mode == "check":
        d = json.load(open(sys.argv[2]))
        if "data" not in d:
            print("ERROR", str(d)[:300]); return
        n, tot = len(d["data"]), d.get("count", {}).get("total", len(d["data"]))
        print("TRUNCATED" if n >= 200 and tot > n else "OK", n, "of", tot)

main()
