"""Offline: build Close search request bodies for the 6-month touch pull. No network.

Reads the saved 45-minute meetings (close/m6/meet/*.json), groups calls into 2-day ET windows by start
time, and for each window writes one search body per activity type (sms, call, email). Each body asks for
that activity on the window's leads, from 00:00 ET the day before the window up to the window's end, which
covers the day-before and day-of touches for every call in it.

Usage:  python3 -I prep_bodies.py            -> writes close/m6/body/*.json
        python3 -I prep_bodies.py split FILE -> halves FILE's lead list into FILE_a / FILE_b, removes FILE
"""
import json, glob, os, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
M6 = os.path.join(HERE, "close", "m6")
BODY = os.path.join(M6, "body")
FIELDS = {
    "sms": ["id", "lead_id", "user_id", "direction", "status", "date_created", "date_sent", "text", "template_id", "sequence_id"],
    "call": ["id", "lead_id", "user_id", "direction", "date_created", "duration", "disposition", "outcome_id"],
    "email": ["id", "lead_id", "user_id", "direction", "status", "date_created", "date_sent", "subject", "sequence_id", "sequence_name", "template_id"],
}
DATE_FIELD = {"sms": "date_created", "call": "date_created", "email": "date_created"}


def body(typ, leads, lo, hi):
    ot = "activity." + typ
    return {"query": {"type": "and", "queries": [
        {"type": "object_type", "object_type": ot},
        {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": DATE_FIELD[typ]},
         "condition": {"type": "moment_range", "on_or_after": {"type": "fixed_utc", "value": lo}, "before": {"type": "fixed_utc", "value": hi}}},
        {"type": "field_condition", "field": {"type": "regular_field", "object_type": ot, "field_name": "lead_id"},
         "condition": {"type": "reference", "reference_type": "lead", "object_ids": sorted(leads)}}]},
        "_fields": {ot: FIELDS[typ]}, "_limit": 200, "include_counts": True}


def utc(d):
    return datetime(d.year, d.month, d.day, tzinfo=ET).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build():
    os.makedirs(BODY, exist_ok=True)
    wins = {}
    for f in glob.glob(os.path.join(M6, "meet", "*.json")):
        for m in json.load(open(f))["data"]:
            if not m.get("lead_id"):
                continue
            d = datetime.fromisoformat(m["starts_at"].replace("Z", "+00:00")).astimezone(ET).date()
            w0 = d - timedelta(days=(d - datetime(2026, 5, 1).date()).days % 2)
            wins.setdefault(w0, set()).add(m["lead_id"])
    n = 0
    for w0, leads in sorted(wins.items()):
        lo, hi = utc(w0 - timedelta(days=1)), utc(w0 + timedelta(days=2))
        for typ in FIELDS:
            json.dump(body(typ, leads, lo, hi), open(os.path.join(BODY, f"{typ}_{w0:%Y%m%d}.json"), "w"))
            n += 1
    print(n, "bodies,", len(wins), "windows,", sum(map(len, wins.values())), "lead-windows")


def split(path):
    b = json.load(open(path))
    ref = b["query"]["queries"][2]["condition"]
    ids = ref["object_ids"]
    if len(ids) < 2:
        sys.exit("cannot split a single lead; split the date range by hand")
    stem = path[:-5]
    for suf, part in (("a", ids[: len(ids) // 2]), ("b", ids[len(ids) // 2:])):
        ref["object_ids"] = part
        json.dump(b, open(f"{stem}{suf}.json", "w"))
        print(f"{stem}{suf}.json", len(part), "leads")
    os.remove(path)


def check(name):
    """After a pull: OK if the saved result is complete; else split its body and delete the result."""
    out, bod = os.path.join(M6, "touch", name + ".json"), os.path.join(BODY, name + ".json")
    d = json.load(open(out))
    if "data" not in d:
        print("ERROR", name, str(d)[:300])
        return
    tot = d["count"]["total"]
    if len(d["data"]) >= tot:
        print("OK", name, tot)
        return
    os.remove(out)
    print("TRUNCATED", name, tot, "-> split:")
    split(bod)


def todo():
    """List bodies that have no complete result yet."""
    done = {os.path.basename(f) for f in glob.glob(os.path.join(M6, "touch", "*.json"))}
    for f in sorted(glob.glob(os.path.join(BODY, "*.json"))):
        if os.path.basename(f) not in done:
            print(os.path.basename(f)[:-5])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["split"]:
        split(a[1])
    elif a[:1] == ["check"]:
        check(a[1])
    elif a[:1] == ["todo"]:
        todo()
    else:
        build()
