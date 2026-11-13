# Offline: compact Calendly list_events pages (saved JSON) into cal_events.jsonl. No network.
import json, sys
out = open(sys.argv[1], 'a')
for f in sys.argv[2:]:
    d = json.load(open(f))
    for e in d['collection']:
        c = e.get('cancellation') or {}
        out.write(json.dumps(dict(uri=e["uri"], name=e["name"], event_type=e["event_type"], status=e['status'], start=e['start_time'], created=e['created_at'], updated=e.get('updated_at'),
            hosts=[m.get('user_email') for m in e.get('event_memberships') or []], invitees=e.get('invitees_counter'),
            canceled_by=c.get('canceled_by'), canceler_type=c.get('canceler_type'), cancel_reason=c.get('reason'), canceled_at=c.get('created_at'))) + '\n')
    print(f, len(d['collection']), d['pagination'].get('next_page_token'))
