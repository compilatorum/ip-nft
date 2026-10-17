# Relatório Executivo: Simulação de Taxa Administrativa do ProofGate

## Resumo executivo

A simulação de taxas foi conduzida com quatro modelos comerciais diferenciados:

- A_counted_exec: a taxa conta para o valor do trade e impacta os limites do mandato.
- B_notcounted_exec: a taxa é cobrada sobre a execução, mas não entra no cálculo do limite.
- C_charge_upfront: a taxa é cobrada antes da avaliação e mesmo em runs que falham.
- F_flat_exec: taxa fixa por execução.

Os dados da simulação mostraram que a estratégia mais sustentável é a combinação de B_notcounted_exec + flat fee modesta sobre execuções aprovadas.

## Conclusão principal

A estratégia A_counted_exec reduz a taxa de aprovação quando o trade está perto do limite do mandato. Isso impacta tanto UX quanto eficiência da operação, e pode gerar fricção sem compensação real em receita.

A estratégia C_charge_upfront gera receita imediata, mas cobra mesmo em caso de fail-closed. Isso é do ponto de vista de reputação e experiência, frágil e potencialmente prejudicial ao produto.

A melhor proposta comercial é:
- Taxa percentual prática (0.1% a 0.5%) em volume executado
- Não contar essa taxa nos limites do mandato
- Cobrar taxa fixa baixa somente em execuções aprovadas
- Não cobrar upfront em fail-closed

## Observações por modelo

### A_counted_exec
- Causa perda de aprovação quando o valor da operação fica perto do teto do mandato.
- Diminui o throughput e pode interferir em negócios legítimos que estavam corretamente aprovados.
- Resultado: ruim para operação e pouco sustentável.

### B_notcounted_exec
- Mantém aprovação elevada e preserva a lógica de fail-closed.
- Gera receita sem quebrar o modelo de salvaguarda do capital.
- Resultado: melhor opção para operação real.

### C_charge_upfront
- Gera receita máxima em curto prazo, mas sem considerar risco de falha.
- Pode criar disputa por cobrança mesmo quando o sistema rejeitou o trade.
- Resultado: aceita apenas com reembolso explícito e regra de política de conta total.

### F_flat_exec
- Muito simples e previsível.
- Funciona como complemento para melhorar anti-spam e reduzir abuso de intents.
- Resultado: bom como custo adicional, mas não como regra principal para toda a operação.

## Recomendação comercial

Estrutura recomendada:

- Taxa percentual de 0.1% a 0.5% sobre valor executado
- Taxa flat mínima de 1–2 USDC por execução aprovada
- Taxa não contada nos limites do mandato
- Sem cobrança upfront em execução rejeitada
- Política de reembolso ou crédito quando a falha for do sistema e não do usuário

## Fórmula prática sugerida

FeeTotal = max(flatFee, pct * Amount) ou, melhor ainda:

FeeTotal = pct * Amount

com pct em [0.1%, 0.5%] e flatFee por operação aprovada em [1, 2] USDC.

## Parâmetros finais sugeridos

- Percent fee: 0.15% (safest), 0.3% (balanced), 0.5% (aggressive)
- Flat fee: 1.0 USDC para pequenas operações
- Não contar fee no limite do trade
- apenas cobrar após aprovação

## Arquivos de referência

- detailed: `proofgate-simulator-spreadsheet/administrative_fee_simulation_detailed.csv`
- aggregated: `proofgate-simulator-spreadsheet/administrative_fee_simulation_aggregated.csv`
- script: `proofgate-simulator-spreadsheet/simulate_fee_models.py`
- charts: `proofgate-simulator-spreadsheet/charts/`

## Encerramento

A operação de ProofGate deve cobrar pela execução segura, não por criar um custo artificial que enfraquece o mecanismo de governança. O melhor equilíbrio de lucro, proteção fiduciária e experiência do usuário está em B_notcounted_exec, combinando percent fee e flat fee baixa, sem afetar o fail-closed guardrail.

