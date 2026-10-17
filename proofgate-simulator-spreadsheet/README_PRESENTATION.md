
# ProofGate Simulator — Presentation Workbook

Este arquivo foi gerado para oferecer uma planilha de apresentação baseada na especificação do `PROOFGATE_SIMULATOR_SPA_SPEC.md` e na estrutura do simulador ProofGate / ValueCurator.

Objetivo:
- Visualizar e simular cenários do ProofGate
- Organizar parâmetros de mandato, evidência de mercado, intent do agente e cenários de risco
- Registrar execuções em runs
- Avaliar invariantes C1..C6
- Resumir vereditos e saúde fiduciária
- Possibilitar dashboard executivo em Excel/Google Sheets

Estrutura recomendada da planilha:
- 01_Index
- 02_Config_Mandate
- 03_Market_Evidence
- 04_Agent_Intent
- 05_Scenarios
- 06_Runs
- 07_Invariants_Eval
- 08_Results_Summary
- 09_Health_Report
- 10_Solana_Logs
- Dashboard

Como gerar o arquivo Excel no ambiente local:
1. pip install pandas openpyxl
2. python proofgate-simulator-spreadsheet/proofgate_simulator_presentation_builder.py
3. Abra `proofgate-simulator-spreadsheet/proofgate_simulations_presentation.xlsx`

Importante:
- A criação de um arquivo .xlsx binário direto neste ambiente não é possível via API de escrita sem um processo local de compilação, mas o gerador foi adicionado ao repositório para executar localmente.
- O pipeline de geração foi preparado para produzir um workbook pronto para Excel/Google Sheets.
