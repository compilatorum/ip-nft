# Pricing Models Comparison — Relatório Resumido

Objetivo
- Simular e comparar três modelos de cobrança para a plataforma:
  1. Taxa percentual recorrente sobre AUM (Assets Under Management)
  2. Taxa fixa cobrada em cada depósito
  3. Taxa percentual sobre rendimento (Performance fee)

Premissas usadas na simulação
- Cenários simulados por 12 meses: Conservative, Balanced, Aggressive
- Fee settings:
  - AUM fee: 0.25% ao ano (0.25)
  - Deposit fee: 1 USDC por depósito (mensal)
  - Performance fee: 20% sobre o lucro anual
- Depósitos mensais como fluxo (12 depósitos por ano)

Resultados (síntese)
- Conservative (baixa performance):
  - Start AUM: 100k; monthly deposit 1k; monthly return 0.2%
  - End AUM ≈ 114.5k; Profit ≈ 507 USDC
  - AUM fee revenue ≈ 268 USDC
  - Deposit fee revenue = 12 USDC
  - Performance fee revenue ≈ 101 USDC
  - Conclusão: AUM fee gera mais receita neste regime conservador.

- Balanced (média performance):
  - Start AUM: 500k; monthly deposit 5k; monthly return 0.8%
  - End AUM ≈ 613.6k; Profit ≈ 53.6k
  - AUM fee revenue ≈ 1,392 USDC
  - Deposit fee revenue = 12 USDC
  - Performance fee revenue ≈ 10,720 USDC
  - Conclusão: Performance fee domina em cenários com retornos relevantes.

- Aggressive (alta performance):
  - Start AUM: 200k; monthly deposit 10k; monthly return 2.0%
  - End AUM ≈ 387.8k; Profit ≈ 67.8k
  - AUM fee revenue ≈ 735 USDC
  - Deposit fee revenue = 12 USDC
  - Performance fee revenue ≈ 13,554 USDC
  - Conclusão: Performance fee claramente superior.

Recomendações práticas
- Para produtos onde retorno esperado é baixo/neutral (custody, capital preservation), prefira AUM fee modest (0.15%–0.3%).
- Para estratégias de alto alfa (arbitrage, PIML), performance fee (20% with hurdle/hwm) captures alignment with user returns and may yield much higher revenue.
- Deposit flat fee is a poor primary revenue source unless deposit frequency is high or fee is larger; better used as anti-spam measure or small onboarding fee.

Opções combinadas (sugeridas)
- Hybrid: small AUM fee (0.10%–0.15%) + performance fee (10%–20% over hurdle). This smooths revenue and aligns incentives.
- Add flat deposit fee as anti-spam (1 USDC refundable for small accounts) or tier-based.

Próximos passos
- Run Monte Carlo sensibility sweep varying:
  - AUM fee ∈ [0.05%, 0.5%]
  - Performance fee ∈ [10%, 30%] with/without hurdle and HWM
  - Deposit fee ∈ [0.5, 5 USDC] and deposit frequencies
- Instrumentar métricas em staging: revenue by model, user cohorts, refund rate.

Arquivos gerados
- proofgate-simulator-spreadsheet/pricing_models_simulation_results.csv
- proofgate-simulator-spreadsheet/simulate_pricing_models.py

