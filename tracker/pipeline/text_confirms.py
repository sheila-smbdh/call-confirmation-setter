"""Offline: prospects who confirmed by text (Sheila, Nov 13). No network.

A prospect's own text saying they'll be on the call counts as a confirmation from the time it was sent: after it, no
day-before call or 5:45 cancel is required. The texts are pulled per lead by the runbook (one inline curl per lead);
the run reads them and decides which ones are confirmations.

usage:
  python3 -I text_confirms.py leads DIR    -> DIR/text_check_leads.txt: leads with a day-before call or 5:45 cancel
                                              required (or can't tell), whose texts need checking
  python3 -I text_confirms.py list DIR     -> prints every inbound text on those leads (from DIR/sms_lead_*.json),
                                              one per line: lead_id | sent at (UTC) | text
The run then writes DIR/text_confirms.json:
  {"<lead_id>": {"at": "<UTC ISO time of the confirming text>", "text": "<the text, short>"}}
listing only texts that clearly say they'll attend ("See you Friday!", "I'll be there", "Confirmed"). A question,
a thanks on its own, or a reschedule request is NOT a confirmation. build.py reads the file.
"""
import glob
import json
import os
import sys

mode, DIR = sys.argv[1], sys.argv[2]

if mode == "leads":
    rows = json.load(open(os.path.join(DIR, "calls_new.json")))
    leads = sorted({r["lead_id"] for r in rows if r.get("lead_id")
                    and (r.get("db_required") in ("Yes", "Can't tell") or r.get("r_required") in ("Yes", "Can't tell"))})
    with open(os.path.join(DIR, "text_check_leads.txt"), "w") as fh:
        fh.write("\n".join(leads) + ("\n" if leads else ""))
    print(len(leads), "leads to check")
elif mode == "list":
    for f in sorted(glob.glob(os.path.join(DIR, "sms_lead_*.json"))):
        d = json.load(open(f))
        for s in sorted(d.get("data", []), key=lambda x: x["date_created"]):
            if s.get("direction") in ("inbound", "incoming") and (s.get("text") or "").strip():
                print(f'{s["lead_id"]} | {s["date_created"][:19]} | {" ".join(s["text"].split())[:200]}')
else:
    sys.exit("mode must be leads or list")
