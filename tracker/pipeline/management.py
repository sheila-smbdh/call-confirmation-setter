"""One-time (and on demand): build the Management tab. Not part of the nightly run, which never replaces this tab.

Usage: python3 -I management.py DATA_DIR TODAY OUT.xlsx
It runs export.py first (to get the Calls and Daily column letters), then adds a Management sheet. References to
Calls and Daily go through INDIRECT so they keep working when the nightly run swaps those tabs.
"""
import runpy, sys
from datetime import date, timedelta
D, TODAY, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["export.py", D, OUT, TODAY]
g = runpy.run_path("export.py")
globals().update({k: v for k, v in g.items() if not k.startswith("__")})
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
wb = load_workbook(OUT)
# ======================= Management (v3: sign-off and bonus first, then KPIs, then support) =======================
from openpyxl.formatting.rule import FormulaRule
mg = wb.create_sheet("Management")
bold = Font(name=FONT, bold=True)
T0 = 15                  # first week row
T1 = T0 + 20             # last week row (21 weeks)
HR = T0 - 1              # column headers
GR = T0 - 2              # group headers
# ---- columns: (key, group, header, formula template using {k} placeholders for other columns' letters, number format)
DS, OV, DB, RZ, GT = "Welcome: during-shift bookings", "Welcome: overnight bookings", "Day-before calls", "5:45 resolutions", "100% gate"
dsum = lambda col_: f'SUMIFS(INDIRECT("Daily!{col_}:{col_}"),INDIRECT("Daily!A:A"),">="&$A{{r}},INDIRECT("Daily!A:A"),"<="&$B{{r}})'
rvw = lambda more: f'COUNTIFS(Reviews!$A:$A,$A{{r}}{more})'
ind = lambda g, n: f'INDIRECT("Calls!{C[(g, n)]}:{C[(g, n)]}")'
wdue, wreq, wbt, wot = (ind("Welcome", "Due date"), ind("Welcome", "Required"), ind("Call", "Booking type"), ind("Welcome", "On time"))
cols_ = [
    ("start", "Week", "Week starting (Mon)", None, "mmm d, yyyy"),
    ("end", "Week", "Week ending (Sun)", "={start}{{r}}+6", "mmm d, yyyy"),
    ("status", "Week", "Week status", '=IF({due}{{r}}=0,"No data yet",IF({end}{{r}}+19/24>NOW(),"Week still open (closes "&TEXT({end}{{r}},"ddd mmm d")&")",IF({todo}{{r}}>0,"WAITING: Reviews",IF(OR({aps}{{r}}="",{apj}{{r}}=""),"WAITING: approval","Done"))))', "@"),
    ("aps", "Sign-off and bonus", "Approved: Sheila", None, "@"),
    ("apj", "Sign-off and bonus", "Approved: Jay", None, "@"),
    ("bonus", "Sign-off and bonus", "Recovery bonus to pay ($)", '=IF(LEFT({elig}{{r}},3)="Yes",{shows}{{r}}*{BONUS},0)', '"$"#,##0'),
    ("shows", "Sign-off and bonus", "Recovered calls that showed", None, "0"),
    ("elig", "Sign-off and bonus", "Eligible for recovery bonus?", '=IF({due}{{r}}=0,"No data",IF({todo}{{r}}>0,"WAITING: decide on Reviews tab",IF({gate}{{r}}="No (ramp)","Yes (ramp week, no gate)",{comp}{{r}})))', "@"),
    ("comp", "Sign-off and bonus", "Compliant on call confirmation? (all 3 KPIs met)", '=IF({due}{{r}}=0,"No data",IF({todo}{{r}}>0,"WAITING: decide on Reviews tab",IF(AND({k1m}{{r}}="Yes",{k2m}{{r}}="Yes",{k3m}{{r}}="Yes"),"Yes","No")))', "@"),
    ("k1", "Key KPIs (all 3 must be met)", "KPI 1: Confirmation score (target 100%)", '=IF({due}{{r}}=0,"",({fin}{{r}}+{exc}{{r}})/{due}{{r}})', "0%"),
    ("k1m", "Key KPIs (all 3 must be met)", "KPI 1 met?", '=IF({due}{{r}}=0,"No data",IF({k1}{{r}}>={GATE},"Yes","No"))', "@"),
    ("k2", "Key KPIs (all 3 must be met)", "KPI 2: Speed to lead, during-shift calls within 15 min (target 85%)", '=IF({wdue}{{r}}=0,"",{w15}{{r}}/{wdue}{{r}})', "0%"),
    ("k2m", "Key KPIs (all 3 must be met)", "KPI 2 met?", '=IF({wdue}{{r}}=0,"No data",IF({k2}{{r}}>={SPEED},"Yes","No"))', "@"),
    ("k3", "Key KPIs (all 3 must be met)", "KPI 3: Logging errors you counted as a miss (target 0)", "=" + rvw(',Reviews!$D:$D,"Logging error",Reviews!$H:$H,"Counts as a miss"'), "0"),
    ("k3m", "Key KPIs (all 3 must be met)", "KPI 3 met?", '=IF(COUNTIFS(Reviews!$A:$A,$A{{r}},Reviews!$D:$D,"Logging error",Reviews!$H:$H,"")>0,"Waiting on Reviews",IF({k3}{{r}}=0,"Yes","No"))', "@"),
    ("gate", "Supporting numbers", "Gate counts this week?", '=IF({start}{{r}}>={START_},"Yes","No (ramp)")', "@"),
    ("due", "Supporting numbers", "Checkpoints due (all four types)", "=" + dsum(L(GT, "Checkpoints that count")), "0"),
    ("fin", "Supporting numbers", "Finished", "=" + dsum(L(GT, "Finished")), "0"),
    ("miss", "Supporting numbers", "Missed", "={due}{{r}}-{fin}{{r}}", "0"),
    ("exc", "Supporting numbers", "Misses you excused", "=" + rvw(',Reviews!$D:$D,"Miss",Reviews!$H:$H,"Excused"'), "0"),
    ("cnt", "Supporting numbers", "Misses that count", "={miss}{{r}}-{exc}{{r}}", "0"),
    ("wdue", "Supporting numbers", "During-shift welcome calls due", "=" + dsum(L(DS, "Due")), "0"),
    ("w15", "Supporting numbers", "First dialed within 15 min",
     f'=COUNTIFS({wdue},">="&$A{{{{r}}}},{wdue},"<="&$B{{{{r}}}},{wreq},"Yes",{wbt},"During shift",{wot},"Yes")', "0"),
    ("lerr", "Supporting numbers", "Logging errors (all)", "=" + rvw(',Reviews!$D:$D,"Logging error"'), "0"),
    ("todo", "Supporting numbers", "Reviews still to decide (this week)", "=" + rvw(',Reviews!$H:$H,""'), "0"),
    ("notes", "Supporting numbers", "Notes", None, "@"),
]
LET = {k: get_column_letter(i) for i, (k, *_r) in enumerate(cols_, 1)}
assert LET["start"] == "A" and LET["end"] == "B"
GATE, SPEED, BONUS, START_ = "$B$8", "$B$9", "$B$10", "$B$11"
def resolve(f):
    if f is None:
        return None
    f = f.replace("{GATE}", GATE).replace("{SPEED}", SPEED).replace("{BONUS}", BONUS).replace("{START_}", START_)
    for k, v in LET.items():
        f = f.replace("{" + k + "}", v)
    return f.replace("{{r}}", "{r}").replace("{{", "{").replace("}}", "}")

# ---- action panel
RV = "Reviews!$A$2:$A"; RH = "Reviews!$H$2:$H"
nrev = f'COUNTIFS({RV},"<>",{RH},"")'
revrows = f'TEXTJOIN(", ",TRUE,FILTER(ROW({RV}),{RV}<>"",{RH}=""))'
E_, Dd = LET["end"], LET["due"]
def appr(cl):
    cnt = f'COUNTIFS(${E_}${T0}:${E_}${T1},"<="&(NOW()-19/24),${Dd}${T0}:${Dd}${T1},">0",${cl}${T0}:${cl}${T1},"")'
    lst = (f'TEXTJOIN("; ",TRUE,ARRAYFORMULA(FILTER("week of "&TEXT($A${T0}:$A${T1},"mmm d")&" (cell {cl}"&ROW($A${T0}:$A${T1})&")",'
           f'${E_}${T0}:${E_}${T1}+19/24<=NOW(),${Dd}${T0}:${Dd}${T1}>0,${cl}${T0}:${cl}${T1}="")))')
    return cnt, lst
sc, sl = appr(LET["aps"]); jc, jl = appr(LET["apj"])
nxt = f'IFERROR(TEXT(MINIFS(${E_}${T0}:${E_}${T1},${E_}${T0}:${E_}${T1},">="&TODAY()),"ddd mmm d"),"")'
mg["A1"] = f'=IF({nrev}+{sc}+{jc}=0,"ALL DONE: nothing needs Sheila or Jay right now.","ACTION NEEDED: "&({nrev}+{sc}+{jc})&" item(s). See the lines below.")'
mg["A2"] = (f'=IF({nrev}=0,"Reviews (Sheila or Jay): all decisions made.","Reviews (Sheila or Jay): "&{nrev}&" decision(s) needed. Go to the Reviews tab, row(s) "&{revrows}'
            f'&". In column H pick Counts as a miss or Excused, and give a reason in column I. The row turns white once decided.")')
mg["A3"] = f'=IF({sc}=0,"Sheila: nothing to approve yet. The current week closes "&{nxt}&".","Sheila: approve "&{sl}&". Choose Approved in that cell once the reviews for that week are decided.")'
mg["A4"] = f'=IF({jc}=0,"Jay: nothing to approve yet. The current week closes "&{nxt}&".","Jay: approve "&{jl}&". Choose Approved in that cell once the reviews for that week are decided.")'
mg["A1"].font = Font(name=FONT, bold=True, size=14)
for r_ in (2, 3, 4):
    mg.cell(r_, 1).font = Font(name=FONT, size=11)
mg.conditional_formatting.add("A1:I1", FormulaRule(formula=['LEFT($A$1,6)="ACTION"'], fill=PatternFill("solid", fgColor="F4B6B6"), font=Font(bold=True, color="9C0006")))
mg.conditional_formatting.add("A1:I1", FormulaRule(formula=['LEFT($A$1,8)="ALL DONE"'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(bold=True, color="006100")))
okf = 'NOT(AND(ISERROR(SEARCH("all decisions made",$A2)),ISERROR(SEARCH("nothing to approve",$A2))))'
mg.conditional_formatting.add("A2:I4", FormulaRule(formula=[f'NOT({okf})'], fill=PatternFill("solid", fgColor="FFFF00")))
mg.conditional_formatting.add("A2:I4", FormulaRule(formula=[okf], fill=PatternFill("solid", fgColor="E2EFDA")))

# ---- inputs
mg["A7"] = "Inputs (blue cells: change here, everything below updates)"
mg["A7"].font = bold
inputs = [("KPI 1 target: share of checkpoints finished (after excused misses)", 1.0, "0%", "Source: Sheila, Nov 12 (decisions log: weekly 100% gate)"),
          ("KPI 2 target: share of during-shift welcome calls first dialed within 15 min", 0.85, "0%", "Source: Sheila, Nov 12"),
          ("Recovery bonus per recovered call that shows ($)", 50, '"$"#,##0', "Source: decisions log, section 2"),
          ("Gate counts from the week starting", date(2026, 11, 23), "mmm d, yyyy", "Source: Sheila, Nov 12. Earlier weeks are ramp: recovery bonuses pay without the gate.")]
for i, (lab, v, nf, srcn) in enumerate(inputs, 8):
    mg.cell(i, 1, lab).font = Font(name=FONT)
    c = mg.cell(i, 2, v)
    c.font = Font(name=FONT, color="0000FF")
    c.number_format = nf
    mg.cell(i, 3, srcn).font = Font(name=FONT, italic=True, color="595959")

# ---- table
GF = {"Week": ("1F3864", "FFFFFF", None), "Sign-off and bonus": ("375623", "FFFFFF", "E2EFDA"),
      "Key KPIs (all 3 must be met)": ("BF8F00", "FFFFFF", "FFF2CC"), "Supporting numbers": ("7F7F7F", "FFFFFF", None)}
mg.cell(GR - 1, 1, "Weekly bonus check (one row per Monday-to-Sunday week)").font = bold
start = 1
for j in range(1, len(cols_) + 2):
    if j == len(cols_) + 1 or cols_[j - 1][1] != cols_[start - 1][1]:
        g = cols_[start - 1][1]
        if j - 1 > start:
            mg.merge_cells(start_row=GR, start_column=start, end_row=GR, end_column=j - 1)
        c = mg.cell(GR, start, g)
        c.font = Font(name=FONT, bold=True, color=GF[g][1])
        c.alignment = Alignment(horizontal="center")
        for k in range(start, j):
            mg.cell(GR, k).fill = PatternFill("solid", fgColor=GF[g][0])
        start = j
for j, (k, g, h, f, nf) in enumerate(cols_, 1):
    c = mg.cell(HR, j, h)
    c.font = Font(name=FONT, bold=True, color=GF[g][1])
    c.fill = PatternFill("solid", fgColor=GF[g][0])
    c.alignment = Alignment(wrap_text=True, vertical="top")
    mg.column_dimensions[get_column_letter(j)].width = 14
weeks = [date(2026, 11, 9) + timedelta(days=7 * k) for k in range(21)]   # through the week of Mar 29, 2027
for i, wkd in enumerate(weeks, T0):
    for j, (k, g, h, f, nf) in enumerate(cols_, 1):
        v = wkd if k == "start" else (None if f is None else resolve(f).format(r=i))
        c = mg.cell(i, j, v)
        c.number_format = nf
        c.font = Font(name=FONT, color="0000FF" if (k == "start" or f is None) else "000000",
                      bold=k in ("bonus", "elig", "comp", "k1m", "k2m", "k3m"))
        if GF[g][2]:
            c.fill = PatternFill("solid", fgColor=GF[g][2])
mg.cell(T0, len(cols_), "Ramp week. Gino started Tue Nov 10; only Nov 10 and 11 are in so far.")
last = T0 + len(weeks) - 1
apv = DataValidation(type="list", formula1='"Approved"', allow_blank=True)
mg.add_data_validation(apv)
A1_, A2_ = LET["aps"], LET["apj"]
apv.add(f"{A1_}{T0}:{A2_}{T1}")
yel, grn, red = PatternFill("solid", fgColor="FFFF00"), PatternFill("solid", fgColor="C6EFCE"), PatternFill("solid", fgColor="F4B6B6")
mg.conditional_formatting.add(f"{A1_}{T0}:{A2_}{T1}", FormulaRule(formula=[f'AND(${E_}{T0}+19/24<=NOW(),${Dd}{T0}>0,{A1_}{T0}="")'], fill=yel))
for key in ("status", "elig", "comp", "k3m"):
    cl = LET[key]
    mg.conditional_formatting.add(f"{cl}{T0}:{cl}{T1}", FormulaRule(formula=[f'LEFT({cl}{T0},7)="WAITING"'], fill=yel))
mg.conditional_formatting.add(f"{LET['status']}{T0}:{LET['status']}{T1}", FormulaRule(formula=[f'{LET["status"]}{T0}="Done"'], fill=grn))
for key in ("elig", "comp", "k1m", "k2m", "k3m"):
    cl = LET[key]
    mg.conditional_formatting.add(f"{cl}{T0}:{cl}{T1}", FormulaRule(formula=[f'LEFT({cl}{T0},3)="Yes"'], fill=grn))
    mg.conditional_formatting.add(f"{cl}{T0}:{cl}{T1}", FormulaRule(formula=[f'{cl}{T0}="No"'], fill=red))
mg.cell(last + 2, 1, "How to read this: the 3 gold KPI columns decide 'Compliant'. Compliant (or a ramp week) makes him eligible, and the bonus is recovered calls that showed x the bonus per call. Grey columns are the supporting numbers.").font = Font(name=FONT, italic=True, color="595959")
mg.cell(last + 3, 1, "Yellow = something for Sheila or Jay to do. It clears on its own once the decision or approval is entered. Recovered calls that showed is typed in for now; it will come from the Recovery tab once that's built.").font = Font(name=FONT, italic=True, color="595959")
mg.column_dimensions["A"].width = 60
mg.column_dimensions["B"].width = 14
mg.column_dimensions[LET["status"]].width = 24
for key in ("elig", "comp"):
    mg.column_dimensions[LET[key]].width = 22
mg.column_dimensions[LET["notes"]].width = 50
mg.row_dimensions[HR].height = 75

# the "last updated" line (row 5): the nightly run writes K5 (its run time, Pacific) and M5 (data through)
mg["J5"], mg["L5"] = "Last refresh (Pacific, set by the update)", "Data through"
DUE = 'IF(AND(WEEKDAY(NOW(),2)<=7,MOD(NOW(),1)>=21/24),INT(NOW())+19/24,INT(NOW())-1+19/24)'
mg["A5"] = ('=IF($K$5="","Last updated: never",IF($K$5<' + DUE + ',"STALE: last updated "&TEXT($K$5+3/24,"ddd mmm d, h:mm AM/PM")&" ET, data through "&TEXT($M$5,"ddd mmm d")&". The daily update should have run by "&TEXT(' + DUE + '+3/24,"ddd mmm d, h:mm AM/PM")&" ET.","Up to date: last updated "&TEXT($K$5+3/24,"ddd mmm d, h:mm AM/PM")&" ET, data through "&TEXT($M$5,"ddd mmm d")&"."))')
mg.conditional_formatting.add("A5:I5", FormulaRule(formula=['LEFT($A$5,5)="STALE"'], fill=red, font=Font(bold=True)))
mg.conditional_formatting.add("A5:I5", FormulaRule(formula=['LEFT($A$5,10)="Up to date"'], fill=grn))
mg.freeze_panes = "A6"
wb.save(OUT)
print("saved", OUT)
