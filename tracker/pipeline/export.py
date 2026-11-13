"""Offline: write the v2 tracker workbook (.xlsx) from calls2.json. No network.
Usage: python3 -I export2.py DIR OUT.xlsx
"""
import json, sys
from datetime import datetime, date
from zoneinfo import ZoneInfo
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

D, OUTF, TODAY_S = sys.argv[1], sys.argv[2], sys.argv[3]
from datetime import timedelta as _td
TODAY = date.fromisoformat(TODAY_S)
from datetime import time as _tm
if datetime.now(ZoneInfo("America/New_York")) < datetime.combine(TODAY, _tm(20, 0), ZoneInfo("America/New_York")):   # mid-shift run: today isn't over yet
    TODAY = TODAY - _td(days=1)
ALL_DAYS = [date(2026, 11, 10) + _td(days=i) for i in range((TODAY - date(2026, 11, 10)).days + 1)]
ET = ZoneInfo("America/New_York")
RUN_AT = datetime.now(ET).strftime("%b %-d, %Y, %-I:%M %p ET")
rows = json.load(open(f"{D}/calls_all.json"))
FONT = "Arial"
HDR = PatternFill("solid", fgColor="1F3864")
FILL = {"Call": "D9E1F2", "Welcome": "E2EFDA", "Day-before": "FFF2CC", "5:45": "FCE4D6", "Check": "EDEDED"}
TITLE = {"Call": "Call", "Welcome": "Welcome call", "Day-before": "Day-before call", "5:45": "5:45 resolution", "Check": "Logging and outcome"}

def dt(s):
    return datetime.fromisoformat(s).astimezone(ET) if s else None

def yn(v):
    return "" if v is None else (v if isinstance(v, str) else ("Yes" if v else "No"))

def headers(ws, groups, fills, titles, hdr_row=2):
    start = 1
    for j in range(1, len(groups) + 2):
        if j == len(groups) + 1 or groups[j - 1][0] != groups[start - 1][0]:
            g = groups[start - 1][0]
            if j - 1 > start:
                ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=j - 1)
            c = ws.cell(1, start, titles.get(g, g))
            c.font = Font(name=FONT, bold=True)
            c.alignment = Alignment(horizontal="center")
            for k in range(start, j):
                ws.cell(1, k).fill = PatternFill("solid", fgColor=fills.get(g, "FFFFFF"))
            start = j
    for j, g in enumerate(groups, 1):
        c = ws.cell(hdr_row, j, g[1])
        c.font = Font(name=FONT, bold=True, color="FFFFFF")
        c.fill = HDR
        c.alignment = Alignment(wrap_text=True, vertical="top")

wb = Workbook()
# ======================= Calls =======================
ws = wb.active
ws.title = "Calls"
cols = [("Call", n) for n in ("Lead", "Close lead", "Closer", "Call date", "Call time (ET)", "Call time (lead's time zone)", "Lead time zone",
                             "Booked date (ET)", "Booked time (ET)", "Booking type", "In his queue", "Calendly status",
                             "Cancelled or rescheduled at (ET)", "Cancelled by", "Invite accepted at (ET)", "Invite declined at (ET)", "Invite status now")]
cols += [("Welcome", n) for n in ("Required", "Why", "Due date", "Due time (ET)", "Touched", "First dial (ET)", "Speed to lead (min)", "On time",
                                  "Dials", "Double dial", "Connected", "Voicemail", "Text sent", "Finished", "Drop-off")]
cols += [("Day-before", n) for n in ("Due date (by 5:45pm MT)", "Required", "Why", "Counts toward gate", "Touched", "Dials", "Double dial",
                                     "Connected", "Voicemail", "Text sent", "Finished", "Drop-off")]
cols += [("5:45", n) for n in ("Due date (5:45pm MT)", "Required", "Why", "Counts toward gate", "Result")]
cols += [("Check", n) for n in ("Gino's last Call Confirmation value", "Gino's last call outcome", "Gino's last status change",
                                "Logging check", "Call happened?", "Source")]
C = {k: get_column_letter(j) for j, k in enumerate(cols, 1)}
headers(ws, cols, FILL, TITLE)
rows.sort(key=lambda r: (r["booked_date"], dt(r.get("w_due")) or datetime.max.replace(tzinfo=ET), r["lead_name"]))
dcell = lambda s: date.fromisoformat(s) if s else None
for i, r in enumerate(rows, 3):
    w, b = r.get("w"), r.get("db")
    wd = dt(r.get("w_due")) if r.get("w_required") not in ("No",) and r.get("w_due") else None
    v = {
        ("Call", "Lead"): r["lead_name"],
        ("Call", "Close lead"): f'=HYPERLINK("https://app.close.com/lead/{r["lead_id"]}/","Open in Close")' if r["lead_id"] else "",
        ("Call", "Closer"): r["closer"], ("Call", "Call date"): dcell(r["call_date"]), ("Call", "Call time (ET)"): r["call_et"],
        ("Call", "Call time (lead's time zone)"): r["call_local"], ("Call", "Lead time zone"): r["lead_tz"],
        ("Call", "Booked date (ET)"): dcell(r["booked_date"]), ("Call", "Booked time (ET)"): r["booked_et"],
        ("Call", "Booking type"): r["booking_type"], ("Call", "In his queue"): r["queue"],
        ("Call", "Calendly status"): r["calendly_status"], ("Call", "Cancelled or rescheduled at (ET)"): r["cancelled_at_et"],
        ("Call", "Cancelled by"): r["cancelled_by"], ("Call", "Invite accepted at (ET)"): r["accepted_at"],
        ("Call", "Invite declined at (ET)"): r["declined_at"], ("Call", "Invite status now"): r["invite_now"],
        ("Welcome", "Required"): r["w_required"], ("Welcome", "Why"): r["w_reason"],
        ("Welcome", "Due date"): wd.date() if wd else None, ("Welcome", "Due time (ET)"): wd.strftime("%-I:%M %p") if wd else "",
        ("Welcome", "Touched"): yn(w["touched"]) if w else "",
        ("Welcome", "First dial (ET)"): dt(w["first_dial"]).strftime("%b %-d %-I:%M %p") if w and w.get("first_dial") else "",
        ("Welcome", "Speed to lead (min)"): r.get("w_speed_min") if w else None, ("Welcome", "On time"): yn(w["on_time"]) if w else "",
        ("Welcome", "Dials"): w["dials"] if w else None, ("Welcome", "Double dial"): w["double_dial"] if w else "",
        ("Welcome", "Connected"): yn(w["connected"]) if w else "", ("Welcome", "Voicemail"): yn(w["voicemail"]) if w else "",
        ("Welcome", "Text sent"): yn(w["text"]) if w else "", ("Welcome", "Finished"): yn(w["finished"]) if w else "",
        ("Welcome", "Drop-off"): w["dropoff"] if w else "",
        ("Day-before", "Due date (by 5:45pm MT)"): dcell(r["db_date"]) if r["db_required"] != "No" else None,
        ("Day-before", "Required"): r["db_required"], ("Day-before", "Why"): r.get("db_reason", ""),
        ("Day-before", "Counts toward gate"): r["db_counts"],
        ("Day-before", "Touched"): yn(b["touched"]) if b else "", ("Day-before", "Dials"): b["dials"] if b else None,
        ("Day-before", "Double dial"): b["double_dial"] if b else "", ("Day-before", "Connected"): yn(b["connected"]) if b else "",
        ("Day-before", "Voicemail"): yn(b["voicemail"]) if b else "", ("Day-before", "Text sent"): yn(b["text"]) if b else "",
        ("Day-before", "Finished"): yn(b["finished"]) if b else "", ("Day-before", "Drop-off"): b["dropoff"] if b else "",
        ("5:45", "Due date (5:45pm MT)"): dcell(r["db_date"]) if r.get("r_required") != "No" else None,
        ("5:45", "Required"): r.get("r_required", ""), ("5:45", "Why"): r.get("r_reason", ""),
        ("5:45", "Counts toward gate"): r["r_counts"], ("5:45", "Result"): r.get("r_result", ""),
        ("Check", "Gino's last Call Confirmation value"): r["last_field"], ("Check", "Gino's last call outcome"): r["last_outcome"],
        ("Check", "Gino's last status change"): r["gino_status"], ("Check", "Logging check"): r["check"],
        ("Check", "Call happened?"): r["happened"], ("Check", "Source"): r["happened_src"],
    }
    for j, k in enumerate(cols, 1):
        c = ws.cell(i, j, v.get(k))
        c.font = Font(name=FONT, color="0563C1" if k == ("Call", "Close lead") else "000000")
        if isinstance(v.get(k), date):
            c.number_format = "mmm d, yyyy"
# Hidden last column: the full row data, so the next nightly run can merge without re-pulling history.
JC = len(cols) + 1
ws.cell(2, JC, "Row data (used by the daily update; don't edit)").font = Font(name=FONT, bold=True)
for i, r in enumerate(rows, 3):
    ws.cell(i, JC, json.dumps(r, default=str))
ws.column_dimensions[get_column_letter(JC)].hidden = True
LAST = len(rows) + 2
ws.freeze_panes = "B3"
wide = {"Lead": 22, "Why": 34, "Drop-off": 22, "Logging check": 70, "Gino's last Call Confirmation value": 40, "In his queue": 18,
        "Gino's last status change": 26, "Cancelled or rescheduled at (ET)": 20, "Invite accepted at (ET)": 17, "Invite declined at (ET)": 17}
for j, (g, n) in enumerate(cols, 1):
    ws.column_dimensions[get_column_letter(j)].width = wide.get(n, 13)
ws.row_dimensions[2].height = 45
ws.cell(1, 1).comment = Comment(
    "Source: #call-confirmation Slack alerts, Close (lead status history, meetings, Gino's calls, texts and Call Confirmation field, "
    "calendar Accepted/Declined emails, call transcripts), Calendly (direct discovery event type), #closer-eod. Refreshed by the nightly update, last run "
    + RUN_AT + ". One row per booked call. Rules are on the Definitions tab.", "Claude")

# ======================= Daily (v3: same columns for every category) =======================
dy = wb.create_sheet("Daily")
col = lambda g, n: f"Calls!${C[(g, n)]}:${C[(g, n)]}"
rng = lambda g, n: f"Calls!${C[(g, n)]}$3:${C[(g, n)]}$2000"
WD, WR, WB = col("Welcome", "Due date"), col("Welcome", "Required"), col("Call", "Booking type")
BD, BR, BG = col("Day-before", "Due date (by 5:45pm MT)"), col("Day-before", "Required"), col("Day-before", "Counts toward gate")
RD, RR, RG = col("5:45", "Due date (5:45pm MT)"), col("5:45", "Required"), col("5:45", "Counts toward gate")
CD, HP = col("Call", "Call date"), col("Check", "Call happened?")
spec = [("", "Date", None, "ddd mmm d")]
pos = {}
def add(g, h, f, nf="0"):
    spec.append((g, h, f, nf))
    pos[(g, h)] = get_column_letter(len(spec))
def L(g, h):
    return pos[(g, h)]

def block(g, base, grp, step_rng_filter, extra_speed):
    """base: COUNTIFS criteria string (without closing paren) selecting the checkpoints that count for this category."""
    cnt = lambda more="": f"COUNTIFS({base}{more})"
    f = lambda n, v: f',{col(grp, n)},"{v}"'
    add(g, "Due", "=" + cnt())
    add(g, "Touched", "=" + cnt(f("Touched", "Yes")))
    add(g, "Touched %", f"=IF({L(g,'Due')}{{r}}=0,0,{L(g,'Touched')}{{r}}/{L(g,'Due')}{{r}})", "0%")
    add(g, "Got them on the phone (done)", "=" + cnt(f("Connected", "Yes")))
    add(g, "No answer", "=" + cnt(f("Touched", "Yes") + f("Connected", "No")))
    add(g, "No answer: all 3 steps done", "=" + cnt(f("Connected", "No") + f("Finished", "Yes")))
    add(g, "No answer: all 3 steps %", f"=IF({L(g,'No answer')}{{r}}=0,0,{L(g,'No answer: all 3 steps done')}{{r}}/{L(g,'No answer')}{{r}})", "0%")
    add(g, "Finished", f"={L(g,'Got them on the phone (done)')}{{r}}+{L(g,'No answer: all 3 steps done')}{{r}}")
    add(g, "Finished %", f"=IF({L(g,'Due')}{{r}}=0,0,{L(g,'Finished')}{{r}}/{L(g,'Due')}{{r}})", "0%")
    add(g, "Double dial %", f"=IF(({cnt(f('Double dial','Yes'))}+{cnt(f('Double dial','No'))})=0,0,{cnt(f('Double dial','Yes'))}/({cnt(f('Double dial','Yes'))}+{cnt(f('Double dial','No'))}))", "0%")
    if extra_speed:
        add(g, "On time %", f"=IF({L(g,'Touched')}{{r}}=0,0,{cnt(f('On time','Yes'))}/{L(g,'Touched')}{{r}})", "0%")
        add(g, "Avg speed to lead (min)", f'=IFERROR(AVERAGEIFS({col("Welcome","Speed to lead (min)")},{base}),"")', "0")
    add(g, "Steps missed or not called", '=IFERROR(TEXTJOIN("; ",TRUE,FILTER(' + rng("Call", "Lead") + '&" ("&' + rng(grp, "Drop-off") + '&")",'
        + step_rng_filter + ',' + rng(grp, "Finished") + '="No")),"none")', "@")

wbase = lambda bt: f'{WD},$A{{r}},{WR},"Yes",{WB},"{bt}"'
wfilt = lambda bt: f'{rng("Welcome","Due date")}=$A{{r}},{rng("Welcome","Required")}="Yes",{rng("Call","Booking type")}="{bt}"'
block("Welcome: during-shift bookings", wbase("During shift"), "Welcome", wfilt("During shift"), True)
block("Welcome: overnight bookings", wbase("Overnight"), "Welcome", wfilt("Overnight"), True)
add("Welcome: not counted", "Accepted at booking (no call needed)", f'=COUNTIFS({WD},$A{{r}},{WR},"Accepted at booking")')
add("Welcome: not counted", "Not in his queue", f'=COUNTIFS({WD},$A{{r}},{WR},"Not in his queue")')
block("Day-before calls", f'{BD},$A{{r}},{BR},"Yes",{BG},"Yes"', "Day-before",
      f'{rng("Day-before","Due date (by 5:45pm MT)")}=$A{{r}},{rng("Day-before","Required")}="Yes",{rng("Day-before","Counts toward gate")}="Yes"', False)
add("Day-before calls", "Can't tell if due", f'=COUNTIFS({BD},$A{{r}},{BR},"Can\'t tell")')
add("Day-before calls", "Not in his queue", f'=COUNTIFS({BD},$A{{r}},{BR},"Not in his queue")')
g = "5:45 resolutions"
add(g, "Needed a cancel", f'=COUNTIFS({RD},$A{{r}},{RR},"Yes",{RG},"Yes")')
add(g, "Cancelled", f'=COUNTIFS({RD},$A{{r}},{RR},"Yes",{RG},"Yes",{col("5:45","Result")},"Cancelled")')
add(g, "Not cancelled", f'=COUNTIFS({RD},$A{{r}},{RR},"Yes",{RG},"Yes",{col("5:45","Result")},"Not cancelled")')
add(g, "Cancellation %", f"=IF({L(g,'Needed a cancel')}{{r}}=0,0,{L(g,'Cancelled')}{{r}}/{L(g,'Needed a cancel')}{{r}})", "0%")
add(g, "Cancelled on the day of the call", f'=COUNTIFS({RD},$A{{r}},{RR},"Yes",{col("5:45","Result")},"Cancelled on the day*")')
add(g, "Not cancelled (names)", '=IFERROR(TEXTJOIN("; ",TRUE,FILTER(' + rng("Call", "Lead") + ',' + rng("5:45", "Due date (5:45pm MT)") + '=$A{r},'
    + rng("5:45", "Required") + '="Yes",' + rng("5:45", "Counts toward gate") + '="Yes",' + rng("5:45", "Result") + '="Not cancelled")),"none")', "@")
add(g, "Can't tell if needed", f'=COUNTIFS({RD},$A{{r}},{RR},"Can\'t tell")')
add(g, "Not in his queue", f'=COUNTIFS({RD},$A{{r}},{RR},"Not in his queue")')
DS, OV, DB = "Welcome: during-shift bookings", "Welcome: overnight bookings", "Day-before calls"
add("100% gate", "Checkpoints that count", f"={L(DS,'Due')}{{r}}+{L(OV,'Due')}{{r}}+{L(DB,'Due')}{{r}}+{L(g,'Needed a cancel')}{{r}}")
add("100% gate", "Finished", f"={L(DS,'Finished')}{{r}}+{L(OV,'Finished')}{{r}}+{L(DB,'Finished')}{{r}}+{L(g,'Cancelled')}{{r}}")
add("100% gate", "Gate %", f"=IF({L('100% gate','Checkpoints that count')}{{r}}=0,0,{L('100% gate','Finished')}{{r}}/{L('100% gate','Checkpoints that count')}{{r}})", "0%")
lc = col("Check", "Logging check"); bd = col("Call", "Booked date (ET)")
add("Logging check", "Logged as accepted", f'=COUNTIFS({bd},$A{{r}},{lc},"?*")')
add("Logging check", "Verified in calendar", f'=COUNTIFS({bd},$A{{r}},{lc},"Verified*")')
add("Logging check", "Valid exception (verbal + tech issue)", f'=COUNTIFS({bd},$A{{r}},{lc},"Valid*")')
add("Logging check", "Logging errors", f'=COUNTIFS({bd},$A{{r}},{lc},"Logging error*")')
cg = "Calls on this date in the tracker"
add(cg, "Scheduled", f"=COUNTIFS({CD},$A{{r}})")
add(cg, "Showed", f'=COUNTIFS({CD},$A{{r}},{HP},"Showed*")')
add(cg, "No-show", f'=COUNTIFS({CD},$A{{r}},{HP},"No-show*")')
add(cg, "Cancelled or rescheduled", f'=COUNTIFS({CD},$A{{r}},{HP},"Cancelled")+COUNTIFS({CD},$A{{r}},{HP},"Rescheduled")')
add(cg, "Unknown or needs confirmation", f'=COUNTIFS({CD},$A{{r}},{HP},"Unknown")+COUNTIFS({CD},$A{{r}},{HP},"Needs confirmation")+COUNTIFS({CD},$A{{r}},{HP},"Zoom never started")')
spec.append(("", "Notes", None, "@"))
names = [(gg, h) for gg, h, ff, n in spec]
DF = {DS: "E2EFDA", OV: "C6E0B4", "Welcome: not counted": "EDEDED", DB: "FFF2CC", "5:45 resolutions": "FCE4D6", "100% gate": "D9E1F2",
      "Logging check": "EDEDED", cg: "EDEDED", "": "FFFFFF"}
headers(dy, names, DF, {})
notes = {"2026-11-10": "First day. Jay told Gino to do welcome calls only, so Nov 10 day-before calls and 5:45 cancels (for Nov 11 calls) don't count toward the gate.",
         "2026-11-11": "Day-before and 5:45 columns are for the next day's calls (Friday covers Saturday to Monday calls)."}
for d_ in ALL_DAYS:
    notes.setdefault(d_.isoformat(), "Weekend: no shift. Anything Gino did is still captured." if d_.weekday() >= 5 else "")
for i, d in enumerate([d_.isoformat() for d_ in ALL_DAYS], 3):
    for j, (gg, h, ff, nf) in enumerate(spec, 1):
        v = date.fromisoformat(d) if h == "Date" else (notes[d] if h == "Notes" else ff.format(r=i))
        c = dy.cell(i, j, v)
        c.font = Font(name=FONT, color="0000FF" if h == "Date" else "000000")
        c.number_format = nf
        if h in ("Steps missed or not called", "Not cancelled (names)"):
            c.alignment = Alignment(wrap_text=True, vertical="top")
for j, (gg, h, ff, nf) in enumerate(spec, 1):
    dy.column_dimensions[get_column_letter(j)].width = 45 if h in ("Steps missed or not called", "Not cancelled (names)") else 12
dy.column_dimensions["A"].width = 13
dy.column_dimensions[get_column_letter(len(spec))].width = 70
dy.row_dimensions[2].height = 60
dy.freeze_panes = "B3"

# ======================= Weekly =======================
wk = wb.create_sheet("Weekly")
inwk = lambda c: f'SUMIFS(Daily!${c}:${c},Daily!$A:$A,">="&$A{{r}},Daily!$A:$A,"<="&$B{{r}})'
wcols = [("Week starting (Mon)", date(2026, 11, 9), "mmm d, yyyy"), ("Week ending (Sun)", "=A{r}+6", "mmm d, yyyy")]
for lab, gg in (("During-shift welcome", DS), ("Overnight welcome", OV), ("Day-before", DB)):
    wcols += [(f"{lab}: due", "=" + inwk(L(gg, "Due")), "0"), (f"{lab}: touched", "=" + inwk(L(gg, "Touched")), "0"),
              (f"{lab}: finished", "=" + inwk(L(gg, "Finished")), "0"), (f"{lab}: finished %", None, "0%")]
wcols += [("5:45 cancels needed", "=" + inwk(L("5:45 resolutions", "Needed a cancel")), "0"),
          ("5:45 cancels done", "=" + inwk(L("5:45 resolutions", "Cancelled")), "0"),
          ("Checkpoints that count", "=" + inwk(L("100% gate", "Checkpoints that count")), "0"),
          ("Finished", "=" + inwk(L("100% gate", "Finished")), "0"), ("Gate %", None, "0%"), ("Gate", None, "@"),
          ("Accepted at booking (no call needed)", "=" + inwk(L("Welcome: not counted", "Accepted at booking (no call needed)")), "0"),
          ("Logging errors", "=" + inwk(L("Logging check", "Logging errors")), "0"),
          ("Notes", "Partial week: Gino started Tue Nov 10. Only Nov 10 and 11 are filled in so far. Gate week runs Monday to Sunday.", "@")]
wl = {h: get_column_letter(j) for j, (h, v, nf) in enumerate(wcols, 1)}
for j, (h, v, nf) in enumerate(wcols, 1):
    if v is None and h.endswith("finished %"):
        p = h[: -len(": finished %")]
        v = f"=IF({wl[p + ': due']}{{r}}=0,0,{wl[p + ': finished']}{{r}}/{wl[p + ': due']}{{r}})"
    elif h == "Gate %":
        v = f"=IF({wl['Checkpoints that count']}{{r}}=0,0,{wl['Finished']}{{r}}/{wl['Checkpoints that count']}{{r}})"
    elif h == "Gate":
        v = f'=IF({wl["Gate %"]}{{r}}=1,"Pass","Fail")'
    c = wk.cell(1, j, h)
    c.font = Font(name=FONT, bold=True, color="FFFFFF")
    c.fill = HDR
    c.alignment = Alignment(wrap_text=True, vertical="top")
    wk.column_dimensions[get_column_letter(j)].width = 13
    mondays = [date(2026, 11, 9) + _td(days=7 * k) for k in range((TODAY - date(2026, 11, 9)).days // 7 + 1)]
    for rr, mon in enumerate(mondays, 2):
        vv = mon if j == 1 else v
        c = wk.cell(rr, j, vv.format(r=rr) if isinstance(vv, str) and vv.startswith("=") else
                    ("Week of Nov 9: Gino started Tue Nov 10." if (h == "Notes" and rr == 2) else ("" if h == "Notes" else vv)))
        c.number_format = nf
        c.font = Font(name=FONT, color="0000FF" if j == 1 else "000000")
wk.column_dimensions[get_column_letter(len(wcols))].width = 60
wk.row_dimensions[1].height = 60
wk.freeze_panes = "A2"

# ======================= Definitions =======================
df = wb.create_sheet("Definitions")
defs = [
    ("Which calls count", "Calendly bookings of the direct discovery event type (booked from the Typeform), including Kevin's bookings that show his own title. S2C calls and closer follow-ups are left out. A reschedule creates a new booking and a new row."),
    ("In his queue", "Where Gino could see the booking: a 'NEW CALL BOOKED' alert in #call-confirmation (Slack), and/or the lead moving to 'Needs Confirmation' or 'Needs Confirmation - Reschedule' (his confirmation smart views). 'Not in his queue' means neither happened. Those rows are shown but never count toward his gate."),
    ("Shift", "Monday to Friday, 9:00am to 6:00pm MT (11:00am to 8:00pm ET). All times in this file are ET unless the column says otherwise."),
    ("Booking type", "During shift: booked between 11:00am and 8:00pm ET on a weekday. Overnight: booked any other time; it belongs to the start of his next shift."),
    ("Welcome call: due", "During shift: 15 minutes after booking. Overnight: 30 minutes after his next shift starts (11:30am ET)."),
    ("Accepted at booking", "The prospect accepted the calendar invite before the welcome call was due (and before Gino dialed). No welcome call is needed, so it's left out of the due count."),
    ("Invite accepted / declined at", "From the calendar response emails ('Accepted:' / 'Declined:') that the closer's calendar sends and Close stores on the lead."),
    ("Speed to lead", "Minutes from booking (or from the start of his shift, for overnight bookings) to his first dial on that lead."),
    ("Touched", "At least one outbound dial by Gino on that lead inside the checkpoint's window."),
    ("Double dial", "A second dial within 3 minutes of the first. 'N/A' when the first dial was answered."),
    ("Connected", "A call with a 'Conversation' outcome, a call screener he got through, an answered call of 45 seconds or more with no voicemail, or the prospect calling him back."),
    ("Voicemail / Text sent", "Counted only when he didn't connect. Texts must be sent or delivered; drafts don't count."),
    ("Finished", "Connected, or double dial plus voicemail plus text. Drop-off names the missing steps."),
    ("Day-before call", "Required when the invite isn't accepted at the start of his shift the day before the call and the lead is in his 'Meeting Tomorrow' view (status 'Needs Confirmation'). If Gino removed it from his view by wrongly logging it accepted, it still counts. If he logged it correctly and the prospect declined later, it doesn't."),
    ("Closer / Setter Confirmed", "If the closer or a setter already confirmed the call, he doesn't call (SOP, Nov 13). Once he logs Closer Confirmed or Setter Confirmed, no welcome, day-before call or 5:45 cancel is required."),
    ("Confirmed by text", "If the prospect texts that they'll be on the call (e.g. \"See you Friday!\"), that counts as confirmed from then on: no day-before call or 5:45 cancel is required after it (Sheila, Nov 13). A question, a thanks on its own or a reschedule request doesn't count."),
    ("5:45 resolution", "Required when the invite still isn't accepted at 5:45pm MT the day before. Done = he cancels it in Calendly that day (or sets Call Confirmation to '6. Cancelled – unreachable'). Bookings made that same day are never cancelled, so they don't need it (Sheila, #cc-gino, confirmed Nov 13)."),
    ("Can't tell", "The invite is accepted now but there is no calendar response email to show when. These don't count toward the gate."),
    ("Counts toward gate", "Nov 10 day-before calls and 5:45 cancels don't count: Jay told Gino to do welcome calls only on his first day."),
    ("Weekends", "No shift on Saturday or Sunday, so nothing is due. Weekend bookings are overnight bookings, due at the start of Monday's shift. On Friday he does the day-before call and 5:45 cancel for Saturday calls only. Sunday and Monday calls have no day-before call or 5:45 cancel (SOP, Nov 13). The update still runs every day so anything Gino does on a weekend is captured."),
    ("100% gate", "Every checkpoint that counts must be finished: overnight and during-shift welcome calls, day-before calls and 5:45 cancels. Weekly, Monday to Sunday."),
    ("Logging check", "Every time Gino recorded an invite as accepted (Call Confirmation 1, 3 or 9, the 'Confirmed and Accepted' outcome, or moving the lead to 'Confirmed'), it's checked against the calendar response emails at that moment. Not accepted then: his call transcript is read. Prospect confirmed and had a technical problem accepting = valid exception. Otherwise = logging error. If Sheila or Jay already approved it in #cc-gino, the Reviews row is filled in as Excused with a link."),
    ("Call happened?", "In order: #closer-eod (Nero's EOD posts), then Zoom attendance on the Close meeting. If neither settles it: Unknown, ask Sheila. The EOD Tracker sheet, Sales Tracker and 2M tracker weren't checked in this version."),
]
for j, h in enumerate(["Term", "Meaning"], 1):
    c = df.cell(1, j, h)
    c.font = Font(name=FONT, bold=True, color="FFFFFF")
    c.fill = HDR
for i, (a, b) in enumerate(defs, 2):
    df.cell(i, 1, a).font = Font(name=FONT, bold=True)
    c = df.cell(i, 2, b)
    c.font = Font(name=FONT)
    c.alignment = Alignment(wrap_text=True, vertical="top")
df.column_dimensions["A"].width = 26
df.column_dimensions["B"].width = 110

# ======================= Data Sources =======================
ds = wb.create_sheet("Data Sources")
src = [
    (f"Calls!A2:{get_column_letter(len(cols))}{LAST}", "Slack", "#call-confirmation 'NEW CALL BOOKED' alerts", "Slack connector, run by Claude (nightly update)", "Alerts from the last 4 days, merged with earlier runs", RUN_AT),
    (f"Calls!A2:{get_column_letter(len(cols))}{LAST}", "Calendly", "Scheduled events and invitees, organization-wide", "Calendly connector, run by Claude (nightly update)", "Direct discovery event type, booked in the last 3 days or with a call from 3 days ago to 4 days ahead; older rows kept from earlier runs", RUN_AT),
    (f"Calls!A2:{get_column_letter(len(cols))}{LAST}", "Close", "Lead status changes, 45-minute meetings, Gino's calls, texts and Call Confirmation field history, calendar Accepted/Declined emails, call transcripts", "Close API, read-only, run by Claude (nightly update)", "Last 4 days of Gino's activity; last 30 days of status changes and calendar responses for those leads", RUN_AT),
    (f"Calls!{C[('Check', 'Call happened?')]}3:{C[('Check', 'Source')]}{LAST}", "Slack", "#closer-eod (Nero EOD posts)", "Slack connector, run by Claude (nightly update)", "EOD posts for the last 4 days", RUN_AT),
]
for j, h in enumerate(["Written to", "Source", "Object", "Obtained via", "Query or request", "Run at"], 1):
    c = ds.cell(1, j, h)
    c.font = Font(name=FONT, bold=True, color="FFFFFF")
    c.fill = HDR
for i, row in enumerate(src, 2):
    for j, v in enumerate(row, 1):
        c = ds.cell(i, j, v)
        c.font = Font(name=FONT)
        c.alignment = Alignment(wrap_text=True, vertical="top")
for j, w in enumerate([20, 10, 42, 24, 60, 24], 1):
    ds.column_dimensions[get_column_letter(j)].width = w

wb.save(OUTF)
print("saved", OUTF, len(rows), "rows;", len(cols), "Calls columns;", len(spec), "Daily columns")
