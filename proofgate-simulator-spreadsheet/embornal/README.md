# Embornal Simulation — README

Este simulador adapta o framework de simulação anterior ao caso de uso "Embornal Cibereconomico Autoregenerativo" descrito em PROOFGATE_B2C_EMBORNAL_CIBERECONOMICO_AUTOREGENERATIVO.md.

Objetivos
- Modelar um micro-fundo (embornal) iniciado com 15.000 USDC, DCA mensal, cesta de ativos ReFi/Phygital
- Simular choque de mercado no mês 7 e mecanismo de autoregeneração (rebalance para ativos resilientes)
- Calcular o índice RWI (Regenerative Wealth Index) combinado com um índice de saúde ecológica
- Integrar cobrança de taxas (AUM fee, deposit fee, performance fee) para estimar impacto econômico

Como rodar
- Requisitos: Python 3.8+, pip
- Instalar libs: pip install pandas numpy
- Rodar exemplo:
  python proofgate-simulator-spreadsheet/simulate_embornal.py --n-sims 5000 --months 12 --out-dir proofgate-simulator-spreadsheet/embornal/out

Saídas
- proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_summary.csv
- proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_detail_sample.csv

Interpretando os resultados
- A coluna 'profit' indica lucro líquido após depósitos, fees e performance fees.
- 'rwi' nas séries mensais é o índice combinando retorno e eco-health.
- Use os primeiros 5 simulações para validar trajetórias; os summaries agregam as distribuições.

Próximos passos sugeridos
- Rodar análise estatística (script de análise)
- Gerar gráficos: a) histograma de profit, b) boxplot de RWI por mês, c) trajectories de AUM
- Ajustar parâmetros: choque severity, regen_strength, fee params e observar trade-offs
