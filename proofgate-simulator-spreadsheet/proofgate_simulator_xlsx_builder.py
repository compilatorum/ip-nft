"""proofgate_simulator_xlsx_builder.py
Gera um arquivo Excel rico proofgate_simulations_advanced.xlsx a partir dos CSVs na pasta proofgate-simulator-spreadsheet.
Recursos incluídos:
- Tabelas Excel (openpyxl Table)
- Validação de dados (dropdowns) para MandateID, EvidenceID, IntentID, Mode, Direction
- Formatação condicional: Verdict (verde/vermelho), HealthIndex (escala de cor)
- Fórmulas para avaliação de invariantes (C1..C6) inseridas na aba 06_Runs
- Dashboard com gráficos (Bar chart: Verdict counts; Scatter: OracleAge vs Divergence) usando dados agregados

Dependências:
- pandas
- openpyxl

Uso:
1) pip install pandas openpyxl
2) python proofgate_simulator_xlsx_builder.py
3) Abra proofgate_simulations_advanced.xlsx
"""

import os
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import PatternFill, Font
from openpyxl.chart import BarChart, Reference, ScatterChart, Series
from openpyxl.chart.marker import DataPoint

BASE_DIR = os.path.dirname(__file__)
CSV_DIR = BASE_DIR
OUT_XLSX = os.path.join(BASE_DIR, "proofgate_simulations_advanced.xlsx")

# CSV files mapping
csv_files = [
    ("01_Index.csv", "01_Index"),
    ("02_Config_Mandate.csv", "02_Config_Mandate"),
    ("03_Market_Evidence.csv", "03_Market_Evidence"),
    ("04_Agent_Intent.csv", "04_Agent_Intent"),
    ("05_Scenarios.csv", "05_Scenarios"),
    ("06_Runs.csv", "06_Runs"),
    ("07_Invariants_Eval.csv", "07_Invariants_Eval"),
    ("08_Results_Summary.csv", "08_Results_Summary"),
    ("09_Health_Report.csv", "09_Health_Report"),
    ("10_Solana_Logs.csv", "10_Solana_Logs"),
]

# Read CSVs into pandas DataFrames
dfs = {}
for fname, sheet in csv_files:
    path = os.path.join(CSV_DIR, fname)
    if os.path.exists(path):
        dfs[sheet] = pd.read_csv(path, dtype=str).fillna("")
    else:
        dfs[sheet] = pd.DataFrame()

# Create workbook
wb = Workbook()
# Remove default sheet
default_sheet = wb.active
wb.remove(default_sheet)

# Helper to write DataFrame to sheet and create an Excel Table
def write_df_as_table(wb, sheet_name, df, table_name=None):
    ws = wb.create_sheet(title=sheet_name)
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
    if df.shape[0] > 0:
        last_col = ws.max_column
        last_row = ws.max_row
        if not table_name:
            table_name = f"tbl_{sheet_name}"
        ref = f"A1:{chr(64+last_col)}{last_row}"
        table = Table(displayName=table_name, ref=ref)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        table.tableStyleInfo = style
        ws.add_table(table)
    # Freeze header
    ws.freeze_panes = "A2"
    return ws

# Write sheets
sheets_written = {}
for sheet_name, df in dfs.items():
    ws = write_df_as_table(wb, sheet_name, df, table_name=f"tbl_{sheet_name}")
    sheets_written[sheet_name] = ws

# Add a helper sheet for dashboard aggregations
if '08_Results_Summary' in dfs and not dfs['08_Results_Summary'].empty:
    res_df = dfs['08_Results_Summary']
else:
    res_df = pd.DataFrame()

data_helper = wb.create_sheet(title="Data_For_Dashboard")
# Compute simple KPIs using direct formulas referencing 06_Runs
# Place header
data_helper.append(["KPI", "Value"])
# TotalRuns
data_helper.append(["TotalRuns", "=COUNTA('06_Runs'!$A:$A)-1"])  # subtract header
# ApprovedRuns
data_helper.append(["ApprovedRuns", "=COUNTIF('06_Runs'!$S:$S, \"APPROVED\")"]) 
# FailRuns
data_helper.append(["FailRuns", "=COUNTIF('06_Runs'!$S:$S, \"FAIL_CLOSED\")"]) 
# ApprovalRate
data_helper.append(["ApprovalRate", "=IF(B2>0, B3 / B2, 0)"]) 
# AvgHealthIndex (from 09_Health_Report column B)
data_helper.append(["AvgHealthIndex", "=IF(COUNTA('09_Health_Report'!$B:$B)>0, AVERAGE('09_Health_Report'!$B:$B), \"\")"]) 
# TotalCapitalProtected
data_helper.append(["TotalCapitalProtectedUsdc", "=SUM('06_Runs'!$U:$U)"])

# Create charts on a Dashboard sheet
dash = wb.create_sheet(title="Dashboard")
# KPI text
dash['A1'] = "ProofGate Simulator Dashboard"
dash['A1'].font = Font(size=14, bold=True)
# Link KPI values
dash['A3'] = "Total Runs"
dash['B3'] = "=Data_For_Dashboard!B2"
dash['A4'] = "Approved Runs"
dash['B4'] = "=Data_For_Dashboard!B3"
dash['A5'] = "Failed Runs"
dash['B5'] = "=Data_For_Dashboard!B4"
dash['A6'] = "Approval Rate"
dash['B6'] = "=Data_For_Dashboard!B5"
dash['A7'] = "Avg Health Index"
dash['B7'] = "=Data_For_Dashboard!B6"

# Bar chart: Verdict counts (Approved vs Fail)
chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "Verdict Counts"
chart.x_axis.title = "Verdict"
chart.y_axis.title = "Count"
# Place source data in helper area
data_helper.append(["Verdict","Count"])  # header row
data_helper.append(["APPROVED","=COUNTIF('06_Runs'!$S:$S, \"APPROVED\")"]) 
data_helper.append(["FAIL_CLOSED","=COUNTIF('06_Runs'!$S:$S, \"FAIL_CLOSED\")"]) 
# Chart references (Data_For_Dashboard last two rows)
last_row = data_helper.max_row
cats = Reference(data_helper, min_col=1, min_row=last_row-1, max_row=last_row)
vals = Reference(data_helper, min_col=2, min_row=last_row-1, max_row=last_row)
chart.add_data(vals, titles_from_data=False)
chart.set_categories(cats)
chart.shape = 4
dash.add_chart(chart, "D3")

# Scatter chart: OracleAge vs Divergence from 06_Runs (columns I and J)
# Build data range references; note: scatter charts require numeric ranges
runs_ws = sheets_written.get('06_Runs')
if runs_ws:
    max_row = runs_ws.max_row
    if max_row >= 2:
        x_ref = Reference(runs_ws, min_col=9, min_row=2, max_row=max_row)  # OracleAge_s I
        y_ref = Reference(runs_ws, min_col=10, min_row=2, max_row=max_row)  # Divergence_bps J
        sc = ScatterChart()
        sc.title = "Oracle Age vs Divergence"
        sc.style = 13
        sc.x_axis.title = "Oracle Age (s)"
        sc.y_axis.title = "Divergence (bps)"
        series = Series(y_ref, xvalues=x_ref)
        sc.series.append(series)
        dash.add_chart(sc, "D20")

# Data validation lists: MandateID, EvidenceID, IntentID, Mode, Direction
from openpyxl.worksheet.datavalidation import DataValidation

# Prepare list strings by reading values from respective sheets
def make_list_range(ws, col_letter):
    # Collect non-header values
    vals = []
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=ws.max_column):
        # Not robust generic; instead read column by letter index
        pass

# Better: create named ranges by copying unique column values into hidden sheet
hidden = wb.create_sheet(title="_lists")
hidden.sheet_state = 'hidden'
# MandateID -> from 02_Config_Mandate col A
mandates = [cell.value for cell in sheets_written['02_Config_Mandate']['A']][1:]
mandates = [m for m in mandates if m]
for i, v in enumerate(mandates, start=1):
    hidden.cell(row=i, column=1).value = v
# EvidenceID -> 03_Market_Evidence col A
evidence = [cell.value for cell in sheets_written['03_Market_Evidence']['A']][1:]
evidence = [e for e in evidence if e]
for i, v in enumerate(evidence, start=1):
    hidden.cell(row=i, column=2).value = v
# IntentID -> 04_Agent_Intent col A
intents = [cell.value for cell in sheets_written['04_Agent_Intent']['A']][1:]
intents = [it for it in intents if it]
for i, v in enumerate(intents, start=1):
    hidden.cell(row=i, column=3).value = v
# Modes and Directions
hidden.cell(row=1, column=5).value = "WASM"
hidden.cell(row=2, column=5).value = "RPC"
hidden.cell(row=1, column=6).value = "BUY"
hidden.cell(row=2, column=6).value = "SELL"

# Define DataValidations using the hidden ranges
# MandateID validation for 06_Runs column E
dv_mandate = DataValidation(type="list", formula1="=_lists!$A$1:$A${n}".format(n=len(mandates)), allow_blank=False)
# EvidenceID validation for 06_Runs column F
dv_evidence = DataValidation(type="list", formula1="=_lists!$B$1:$B${n}".format(n=len(evidence)), allow_blank=False)
# IntentID validation for 06_Runs column G
dv_intent = DataValidation(type="list", formula1="=_lists!$C$1:$C${n}".format(n=len(intents)), allow_blank=False)
# Mode validation
dv_mode = DataValidation(type="list", formula1='="WASM,RPC"', allow_blank=False)
# Direction validation
dv_direction = DataValidation(type="list", formula1='="BUY,SELL"', allow_blank=False)

# Add validations to the runs sheet
runs_ws = sheets_written.get('06_Runs')
if runs_ws:
    runs_ws.add_data_validation(dv_mandate)
    runs_ws.add_data_validation(dv_evidence)
    runs_ws.add_data_validation(dv_intent)
    runs_ws.add_data_validation(dv_mode)
    runs_ws.add_data_validation(dv_direction)
    # apply to a reasonable range (rows 2..500)
    dv_mandate.add(f"E2:E500")
    dv_evidence.add(f"F2:F500")
    dv_intent.add(f"G2:G500")
    dv_mode.add(f"D2:D500")
    # Direction is in Agent_Intent sheet col F; add there
    dv_direction.add("04_Agent_Intent!$F$2:$F$500")

# Conditional formatting for Verdict column (S) in Runs
if runs_ws:
    green = PatternFill(start_color='065f46', end_color='065f46', fill_type='solid')
    red = PatternFill(start_color='7f1d1d', end_color='7f1d1d', fill_type='solid')
    # APPROVED -> green
    runs_ws.conditional_formatting.add(f"S2:S500", FormulaRule(formula=["$S2=\"APPROVED\""], stopIfTrue=True, fill=green))
    # FAIL_CLOSED -> red
    runs_ws.conditional_formatting.add(f"S2:S500", FormulaRule(formula=["$S2=\"FAIL_CLOSED\""], stopIfTrue=True, fill=red))

# Conditional formatting for HealthIndexScore in 09_Health_Report column B
health_ws = sheets_written.get('09_Health_Report')
if health_ws:
    # Color scale: green -> yellow -> red
    health_ws.conditional_formatting.add("B2:B500", ColorScaleRule(start_type='num', start_value=0.95, start_color='006400', mid_type='num', mid_value=0.5, mid_color='FFFF00', end_type='num', end_value=0.0, end_color='9C0006'))

# Insert invariant evaluation formulas in 06_Runs (similar to previous script)
if runs_ws:
    max_row = runs_ws.max_row
    for r in range(2, max_row + 1):
        # I (9): OracleAge_s
        runs_ws[f"I{r}"].value = f"=IFERROR(INDEX('03_Market_Evidence'!$L:$L, MATCH($F{r}, '03_Market_Evidence'!$A:$A, 0)), \"\")"
        # J (10): Divergence_bps
        runs_ws[f"J{r}"].value = f"=IFERROR(INDEX('03_Market_Evidence'!$M:$M, MATCH($F{r}, '03_Market_Evidence'!$A:$A, 0)), \"\")"
        # K (11): Confidence_bps
        runs_ws[f"K{r}"].value = f"=IFERROR(INDEX('03_Market_Evidence'!$N:$N, MATCH($F{r}, '03_Market_Evidence'!$A:$A, 0)), \"\")"
        # L (12): PriceImpact_bps
        runs_ws[f"L{r}"].value = f"=IFERROR(INDEX('03_Market_Evidence'!$G:$G, MATCH($F{r}, '03_Market_Evidence'!$A:$A, 0)), \"\")"
        # M (13): Evaluated_C1
        runs_ws[f"M{r}"].value = f"=IFERROR(IF(SEARCH(INDEX('04_Agent_Intent'!$H:$H, MATCH($G{r}, '04_Agent_Intent'!$A:$A, 0)), INDEX('02_Config_Mandate'!$B:$B, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)))>0, TRUE, FALSE), FALSE)"
        # N (14): Evaluated_C2
        runs_ws[f"N{r}"].value = f"=IF(AND(INDEX('04_Agent_Intent'!$C:$C, MATCH($G{r}, '04_Agent_Intent'!$A:$A, 0)) <= INDEX('02_Config_Mandate'!$C:$C, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)), (INDEX('04_Agent_Intent'!$C:$C, MATCH($G{r}, '04_Agent_Intent'!$A:$A, 0)) + INDEX('04_Agent_Intent'!$E:$E, MATCH($G{r}, '04_Agent_Intent'!$A:$A, 0))) <= INDEX('02_Config_Mandate'!$D:$D, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0))), TRUE, FALSE)"
        # O (15): Evaluated_C3
        runs_ws[f"O{r}"].value = f"=IF($I{r} <= INDEX('02_Config_Mandate'!$E:$E, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)), TRUE, FALSE)"
        # P (16): Evaluated_C4
        runs_ws[f"P{r}"].value = f"=IF($K{r} <= INDEX('02_Config_Mandate'!$F:$F, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)), TRUE, FALSE)"
        # Q (17): Evaluated_C5
        runs_ws[f"Q{r}"].value = f"=IF($J{r} <= INDEX('02_Config_Mandate'!$G:$G, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)), TRUE, FALSE)"
        # R (18): Evaluated_C6
        runs_ws[f"R{r}"].value = f"=IF($L{r} <= INDEX('02_Config_Mandate'!$H:$H, MATCH($E{r}, '02_Config_Mandate'!$A:$A, 0)), TRUE, FALSE)"
        # S (19): Verdict
        runs_ws[f"S{r}"].value = f"=IF(AND($M{r}, $N{r}, $O{r}, $P{r}, $Q{r}, $R{r}), \"APPROVED\", \"FAIL_CLOSED\")"
        # T (20): FailureReasons
        runs_ws[f"T{r}"].value = f"=TEXTJOIN(\"; \", TRUE, IF($M{r}, \"\", \"ERR_UNAUTHORIZED_MINT\"), IF($N{r}, \"\", \"ERR_VOLUME_EXCEEDED\"), IF($O{r}, \"\", \"ERR_STALE_ORACLE\"), IF($P{r}, \"\", \"ERR_CONFIDENCE_TOO_WIDE\"), IF($Q{r}, \"\", \"ERR_PRICE_DIVERGENCE\"), IF($R{r}, \"\", \"ERR_EXCESSIVE_SLIPPAGE\"))"
        # U (21): CapitalProtectedUsdc
        runs_ws[f"U{r}"].value = f"=IF($S{r}=\"FAIL_CLOSED\", INDEX('04_Agent_Intent'!$C:$C, MATCH($G{r}, '04_Agent_Intent'!$A:$A, 0)), 0)"

# Save file
wb.save(OUT_XLSX)
print(f"Arquivo gerado: {OUT_XLSX}")
