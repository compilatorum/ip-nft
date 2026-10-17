# Dashboard Instructions

Esta aba contém instruções para criar um dashboard no Excel ou Google Sheets usando os dados das outras abas.

Recomendações de gráficos:
- KPI cards: TotalRuns, ApprovalRate (use células calculadas na aba 08_Results_Summary)
- Time-series: Número de runs por dia (use pivot table na aba 06_Runs)
- Scatter: OracleAge (col I de Runs) vs Divergence_bps (col J), cor por Verdict
- Radar chart: média dos 6 invariantes (use 07_Invariants_Eval agregando por InvariantID)
- Bar chart: frequência de FailureReasons (tokenize T column em 06_Runs e conte ocorrências)

Formatação condicional sugerida:
- 06_Runs: coluna Verdict -> verde para APPROVED, vermelho para FAIL_CLOSED
- 09_Health_Report: HealthIndexScore -> escala de cores (>=0.95 verde escuro, <0.3 vermelho)

Para gerar o Excel:
1. `pip install pandas openpyxl`
2. `python make_spreadsheet.py`
3. Abra `proofgate_simulations.xlsx`

