# ProofGate Simulator Spreadsheet

Este diretório contém a estrutura base da planilha do simulador ProofGate / ValueCurator, em CSVs + script Python para gerar um arquivo Excel (.xlsx) com fórmulas e estrutura pronta para uso em Excel ou Google Sheets.

Estrutura:
- 01_Index.csv
- 02_Config_Mandate.csv
- 03_Market_Evidence.csv
- 04_Agent_Intent.csv
- 05_Scenarios.csv
- 06_Runs.csv
- 07_Invariants_Eval.csv
- 08_Results_Summary.csv
- 09_Health_Report.csv
- 10_Solana_Logs.csv
- 11_Dashboard_Instructions.md
- make_spreadsheet.py

Como gerar a planilha Excel:
1. Instale dependências: `pip install pandas openpyxl`
2. Execute: `python make_spreadsheet.py`
3. Abra o arquivo gerado: `proofgate_simulations.xlsx`

Observações:
- A linha inicial de dados é a linha 6 em todas as abas principais.
- A aba 06_Runs contém fórmulas para avaliar os 6 invariantes (C1 a C6).
- O dashboard pode ser montado com base na aba 08_Results_Summary e nas abas 06_Runs / 07_Invariants_Eval.
