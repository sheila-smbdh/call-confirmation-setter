"""Offline: write the Close search request bodies for one nightly run. No network.

Usage:
  python3 -I bodies.py meetings DATA_DIR TODAY   -> DATA_DIR/body_meet_created.json, body_meet_starts.json
  python3 -I bodies.py leads DATA_DIR TODAY      -> DATA_DIR/body_lsc.json, body_acc.json (needs DATA_DIR/scope.json)
  python3 -I bodies.py recovery DATA_DIR TODAY  -> DATA_DIR/body_rec_lsc.json, body_rec_field.json, body_rec_act.json
  python3 -I bodies.py recovery_leads DATA_DIR TODAY -> body_rec_info.json, body_rec_calls.json, body_rec_sms.json,
                                                  body_rec_meet.json, body_rec_tasks.json (needs the three rec_ results)
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


# ---- call recovery (Sheila, Nov 24): every lead that landed in recovery since REC_FROM, plus leads Gino logged a
# Call Recovery day on (backlog). Results must be saved as rec_<name>.json (e.g. rec_lsc.json, rec_calls.json).
REC_FROM = date(2026, 11, 24)
REC_STATUSES = ["stat_9Y7PGCmmMfaPDCegpeNE6S6sJ73FBsKfjDMKKqQUGyZ",   # No Show - Recovery
                "stat_0aBE25GBxLXaDaXjpF03OOodRiWc0JEBm4vK7be1rLQ",   # Cancelled - Recovery
                "stat_NAWbDcVPEwwcZUcaovamXMN2hZZUJTojae5ix4rc27f"]   # Reschedule Request - Recovery
REC_CF = "cf_Cp9QRtPjlRz2XS2F7cDd4grwWbowcFYPjACyENQKvUT"            # lead field "Call Recovery"
REC_CHOICES = ["Day 1 Recovery - No Pickup, Double Dial, VM, Text", "Day 2 Recovery - No Pickup",
               "Day 3 Recovery - No Pickup, Double Dial, VM, Text", "Day 4 Recovery - No Pickup",
               "Day 5 Recovery - No Pickup, Double Dial, VM, Text", "Not Interested", "Rebooked"]
REC_ACT = "actitype_4amdMgBLIyriwpHWvepeGm"                           # custom activity "Call Confirmation Specialist"

def rec_leads(D):
    leads = set()
    for f in sorted(os.listdir(D)):
        if f.startswith(("rec_lsc", "rec_field", "rec_act")) and f.endswith(".json"):
            for x in json.load(open(f"{D}/{f}")).get("data", []):
                leads.add(x.get("lead_id") or x["id"])
    return leads

def rec_bodies(D, today, stage):
    lo = utc(REC_FROM)
    if stage == 1:
        ot = "activity.lead_status_change"
        q = [{"type": "object_type", "object_type": ot}, rng(ot, "date_created", lo, NOW),
             {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "new_status_id"},
              "condition": {"type": "reference", "reference_type": "status.lead", "object_ids": REC_STATUSES}}]
        json.dump({"query": {"type": "and", "queries": q}, "_limit": 200, "include_counts": True,
                   "_fields": {ot: ["id", "lead_id", "user_id", "date_created", "old_status_label", "new_status_label"]}},
                  open(f"{D}/body_rec_lsc.json", "w"))
        q = [{"type": "object_type", "object_type": "lead"},
             {"type": "field_condition", "field": {"type": "custom_field", "custom_field_id": REC_CF},
              "condition": {"type": "term", "values": REC_CHOICES}}]
        json.dump({"query": {"type": "and", "queries": q}, "_limit": 200, "include_counts": True, "_fields": {"lead": ["id"]}},
                  open(f"{D}/body_rec_field.json", "w"))
        ot = "activity.custom_activity"
        q = [{"type": "object_type", "object_type": ot}, rng(ot, "date_created", lo, NOW),
             {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "custom_activity_type_id"},
              "condition": {"type": "term", "values": [REC_ACT]}}]
        json.dump({"query": {"type": "and", "queries": q}, "_limit": 200, "include_counts": True,
                   "_fields": {ot: ["id", "lead_id", "user_id", "date_created", "custom." + "cf_WXINcug6ED7jvnlix8XebyvKFWMALmNnF9JAMl2JWLH"]}},
                  open(f"{D}/body_rec_act.json", "w"))
        print("wrote body_rec_lsc.json, body_rec_field.json, body_rec_act.json")
        return
    leads = rec_leads(D)
    if not leads:
        print("0 recovery leads; nothing more to pull"); return
    q = [{"type": "object_type", "object_type": "lead"}, {"type": "or", "queries": [{"type": "id", "value": l} for l in sorted(leads)]}]
    info = {"query": {"type": "and", "queries": q}, "_limit": 200, "include_counts": True,
            "_fields": {"lead": ["id", "display_name", "status_label", "contacts", "custom." + REC_CF, "num_incomplete_tasks"]}}
    json.dump(info, open(f"{D}/body_rec_info.json", "w"))
    json.dump(leads_q("activity.call", lo, NOW, leads, fields=["id", "lead_id", "user_id", "date_created", "direction", "disposition",
              "duration", "outcome_id", "voicemail_url", "note", "status"]), open(f"{D}/body_rec_calls.json", "w"))
    gino = {"type": "field_condition", "field": {"type": "regular_field", "object_type": "activity.sms", "field_name": "user_id"},
            "condition": {"type": "reference", "reference_type": "user", "object_ids": ["user_7U4Qw9J25dXEBpvkRXkEJUswf2RLo646IuuPxybyuNo"]}}
    json.dump(leads_q("activity.sms", lo, NOW, leads, gino, ["id", "lead_id", "user_id", "date_created", "direction", "status"]),
              open(f"{D}/body_rec_sms.json", "w"))
    b = leads_q("activity.meeting", lo, NOW, leads, fields=["id", "lead_id", "user_id", "starts_at", "status", "title", "date_created",
                "integrations", "duration"])
    json.dump(b, open(f"{D}/body_rec_meet.json", "w"))
    json.dump(leads_q("task.lead", lo, NOW, leads, fields=["id", "lead_id", "assigned_to", "date_created", "date", "is_complete"]),
              open(f"{D}/body_rec_tasks.json", "w"))
    print(len(leads), "recovery leads; wrote body_rec_info.json, body_rec_calls.json, body_rec_sms.json, body_rec_meet.json, body_rec_tasks.json")

def main():
    mode = sys.argv[1]
    if mode in ("meetings", "leads", "recovery", "recovery_leads"):
        D, today = sys.argv[2], date.fromisoformat(sys.argv[3])
    if mode == "meetings":
        json.dump(meet("date_created", utc(today - timedelta(days=4)), NOW), open(f"{D}/body_meet_created.json", "w"))
        json.dump(meet("starts_at", utc(today - timedelta(days=3)), utc(today + timedelta(days=15))), open(f"{D}/body_meet_starts.json", "w"))
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
    elif mode == "recovery":
        rec_bodies(D, today, 1)
    elif mode == "recovery_leads":
        rec_bodies(D, today, 2)
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
