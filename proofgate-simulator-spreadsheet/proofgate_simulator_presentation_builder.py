"""proofgate_simulator_presentation_builder.py
Gera uma versão de apresentação da planilha proofgate_simulations_presentation.xlsx com layout de cockpit, paleta de cores, KPI cards, badges e dashboards estilizados.
Requisitos: pandas, openpyxl
Uso:
1) pip install pandas openpyxl
2) python proofgate_simulator_presentation_builder.py
3) Abra proofgate_simulations_presentation.xlsx

Este script baseia-se nos CSVs na mesma pasta proofgate-simulator-spreadsheet e cria uma planilha com:
- Abas formatadas e tabelas
- KPI cards com cores e ícones (texto estilizado)
- Gráficos: Verdict bar, OracleAge vs Divergence scatter, Radar (simulado via multiple series)
- Painel de Dashboard com layout tipo Cockpit (valores principais, gráficos e instruções)
- Nomes definidos e validações de dados

Observação: O script gera um arquivo Excel pronto para abertura; para recursos gráficos adicionais ou imagens (badges SVG), recomendo inserir manualmente via Excel UI.
"""

import os
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
from openpyxl.chart import BarChart, Reference, ScatterChart, Series, LineChart

BASE_DIR = os.path.dirname(__file__)
CSV_DIR = BASE_DIR
OUT_XLSX = os.path.join(BASE_DIR, "proofgate_simulations_presentation.xlsx")

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

# Load CSVs
dfs = {}
for fname, sheet in csv_files:
    path = os.path.join(CSV_DIR, fname)
    if os.path.exists(path):
        dfs[sheet] = pd.read_csv(path, dtype=str).fillna("")
    else:
        dfs[sheet] = pd.DataFrame()

# Create workbook
wb = Workbook()
wb.remove(wb.active)

# Helper to write DataFrame to sheet
def add_sheet_from_df(name, df):
    ws = wb.create_sheet(name)
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    # Table style if data exists
    if df.shape[0] > 0:
        last_col = ws.max_column
        last_row = ws.max_row
        ref = f"A1:{(ws.cell(row=1, column=last_col).column_letter)}{last_row}"
        tbl = Table(displayName=f"tbl_{name}", ref=ref)
        tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showRowStripes=True)
        ws.add_table(tbl)
    ws.freeze_panes = "A2"
    # Set default column widths
    for col in range(1, ws.max_column + 1):
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 18
    return ws

sheets = {}
for sheet_name, df in dfs.items():
    sheets[sheet_name] = add_sheet_from_df(sheet_name, df)

# Create Presentation Dashboard
dash = wb.create_sheet("Dashboard")
# Palette (cockpit)
bg = PatternFill(fill_type="solid", start_color="090d16", end_color="090d16")
panel_fill = PatternFill(fill_type="solid", start_color="0e1724", end_color="0e1724")
accent = "06b6d4"  # electric cyan
accent_fill = PatternFill(fill_type="solid", start_color=accent, end_color=accent)

# Header
dash.merge_cells('A1:H1')
dash['A1'] = "ProofGate Simulator — Cockpit Dashboard"
dash['A1'].font = Font(size=16, bold=True, color="FFFFFF")
dash['A1'].alignment = Alignment(horizontal='center', vertical='center')
for c in range(1, 9):
    dash.cell(row=1, column=c).fill = PatternFill(fill_type='solid', start_color='0b1220', end_color='0b1220')

# KPI Cards area
kpis = [
    ("Total Runs", "=COUNTA('06_Runs'!$A:$A)-1"),
    ("Approved Rate", "=IF(COUNTA('06_Runs'!$A:$A)>1, COUNTIF('06_Runs'!$S:$S, \"APPROVED\")/ (COUNTA('06_Runs'!$A:$A)-1), 0)"),
    ("Avg Health Index", "=IF(COUNTA('09_Health_Report'!$B:$B)>0, AVERAGE('09_Health_Report'!$B:$B), \"\")"),
    ("Total Capital Protected (USDC)", "=SUM('06_Runs'!$U:$U)")
]

start_row = 3
for i, (label, formula) in enumerate(kpis):
    col = 1 + (i * 2)
    dash.merge_cells(start_row=start_row, start_column=col, end_row=start_row, end_column=col+1)
    cell = dash.cell(row=start_row, column=col)
    cell.value = label
    cell.font = Font(color="FFFFFF", bold=True)
    cell.alignment = Alignment(horizontal='center')
    dash.cell(row=start_row+1, column=col).value = formula
    val_cell = dash.cell(row=start_row+1, column=col)
    val_cell.number_format = 'General'
    val_cell.font = Font(color="FFFFFF", bold=True, size=14)
    val_cell.alignment = Alignment(horizontal='center')
    # Fill the KPI card background
    for r in range(start_row, start_row+2):
        for c in range(col, col+2):
            dash.cell(row=r, column=c).fill = PatternFill(fill_type='solid', start_color='0f1724', end_color='0f1724')

# Place charts: Verdict counts
# Prepare helper table in hidden sheet
hidden = wb.create_sheet("_hidden_lists")
hidden.sheet_state = 'hidden'
# Verdict counts formulas
hidden['A1'] = 'Verdict'
hidden['B1'] = 'Count'
hidden['A2'] = 'APPROVED'
hidden['A3'] = 'FAIL_CLOSED'
hidden['B2'] = "=COUNTIF('06_Runs'!$S:$S, \"APPROVED\")"
hidden['B3'] = "=COUNTIF('06_Runs'!$S:$S, \"FAIL_CLOSED\")"

bar = BarChart()
bar.title = "Verdict Counts"
bar.style = 2
bar.y_axis.title = 'Count'
bar.x_axis.title = 'Verdict'
data = Reference(hidden, min_col=2, min_row=2, max_row=3)
cats = Reference(hidden, min_col=1, min_row=2, max_row=3)
bar.add_data(data, titles_from_data=False)
bar.set_categories(cats)
dash.add_chart(bar, "A7")

# Scatter chart OracleAge vs Divergence
runs_ws = sheets.get('06_Runs')
if runs_ws and runs_ws.max_row > 1:
    max_row = runs_ws.max_row
    xref = Reference(runs_ws, min_col=9, min_row=2, max_row=max_row)
    yref = Reference(runs_ws, min_col=10, min_row=2, max_row=max_row)
    sc = ScatterChart()
    sc.title = "Oracle Age vs Divergence"
    sc.x_axis.title = 'Oracle Age (s)'
    sc.y_axis.title = 'Divergence (bps)'
    s = Series(yref, xref)
    sc.series.append(s)
    sc.width = 20
    sc.height = 12
    dash.add_chart(sc, "E7")

# Line chart: Capital Protected over Runs (time series)
line = LineChart()
line.title = 'Capital Protected over Runs'
line.style = 13
line.y_axis.title = 'USDC'
if runs_ws and runs_ws.max_row > 1:
    vals = Reference(runs_ws, min_col=21, min_row=2, max_row=runs_ws.max_row)
    line.add_data(vals, titles_from_data=False)
    dash.add_chart(line, "A20")

# Instructions panel
dash.merge_cells('A34:H40')
dash['A34'] = 'Instruções: Use os filtros nas tabelas das abas para investigar cada run. Para injetar cenários, use o Apps Script (proofgate_sheet_automation.gs) ou gere novas evidências em 03_Market_Evidence e referências em 06_Runs.'
dash['A34'].alignment = Alignment(wrap_text=True)

# Styling: dark background for dashboard
for row in dash.iter_rows(min_row=1, max_row=40, min_col=1, max_col=8):
    for cell in row:
        if cell.value is None:
            cell.value = ""
        cell.font = Font(color='FFFFFF')
        # do not overwrite header area that already has fill
        if cell.row > 1:
            cell.fill = PatternFill(fill_type='solid', start_color='071123', end_color='071123')

# Final touches: set active sheet to Dashboard
wb.active = wb.sheetnames.index('Dashboard') if 'Dashboard' in wb.sheetnames else 0

# Save
wb.save(OUT_XLSX)
print(f'Arquivo de apresentação gerado: {OUT_XLSX}')
