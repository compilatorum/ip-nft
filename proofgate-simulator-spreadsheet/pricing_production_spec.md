# Pricing Production Specification — ProofGate / ValueCurator

Este documento define a política de pricing final para produção, configurações operacionais, API/SDK snippets e critérios de monitoramento/rollback.

Resumo executivo
- Modelo principal: B_notcounted_exec — taxa percentual cobrada apenas sobre valor executado (não contada nos limites do mandato).
- Complemento: flat fee por execução aprovada para controle de spam e receita base.
- Política de cobrança: taxa somente cobrada após veredito APPROVED e execução bem-sucedida (ou assinatura do recibo). Em casos excepcionais de cobrança antecipada (anti-spam), reembolso automático para FAIL_CLOSED.

Parâmetros recomendados iniciais (configuração padrão)
- percentFeePctDefault: 0.15% (0.0015)
- percentFeePctOptions: [0.10%, 0.15%, 0.30%] — para A/B testing
- flatFeeUsdcDefault: 1.00 USDC
- flatFeeVerifiedUsdc: 0.50 USDC (redução para usuários verificados)
- minFeeUsdc: 0.10 USDC
- maxFeePctCap: 1.00% (0.01) — teto para evitar taxas confiscatórias
- feeCurrency: USDC (liquidity/custody in PDA)

Fee accounting rules
- Fee is charged in USDC equivalent at time of execution.
- Fee does NOT increment the effective trade amount for invariant checks (B_notcounted_exec).
- Collect fee only after the gate returns APPROVED and the on-chain simulation or actual execution succeeds (depends on mode WASM vs RPC).
- For flat fees, if the run fails post-approval due to infrastructure error, the flat fee must be refunded.
- Maintain ledger entries per run:
  - ledger: { runId, userId, amountUsdc, feePct, feeUsdc, flatFeeUsdc, feeCollectedAt, verdict, txSignature (if any), refunded (bool), refundTxSig }

Tiering & discounts
- Volume tiers (optional): users with volume > X per 30d may get discount on percentFee (e.g., -10% on pct) and lower flat fee.
- Verified users (KYC/whitelisted) can have reduced flatFeeUsdc and faster dispute handling.

Anti-abuse & spam mitigation
- Rate limiting: default 10 intents/min per account; adjustable per user tier.
- Anti-spam flat fee: if the account exceeds a spike threshold (e.g., >50 intents/hour), apply higher flat fee (2–5 USDC) until behavior normalizes.
- Minimum computational deposit: for unknown accounts require a pre-authorized small refundable deposit (0.5 USDC) to prevent bots.

Refund & dispute policy
- If fee was charged but the run is FAIL_CLOSED (and fee was charged upfront), automatic refund must be issued within 24h.
- If a successful APPROVED run afterwards fails at execution due to infra (not user), refund full fee and mark ledger.refunded=true.
- Provide programmatic dispute creation endpoint that stores dispute metadata and alerts ops.

Implementation details (TypeScript / TS config)
- Location: src/config/pricing.ts and src/lib/fee.ts (core logic)

File: src/config/pricing.ts
```ts
export const PRICING = {
  percentFeePctDefault: 0.15 / 100, // 0.0015
  percentFeePctOptions: [0.001, 0.0015, 0.003],
  flatFeeUsdcDefault: 1.0,
  flatFeeVerifiedUsdc: 0.5,
  minFeeUsdc: 0.1,
  maxFeePctCap: 0.01,
  feeCurrency: 'USDC',
  antiSpam: {
    defaultRateLimitPerMin: 10,
    spikeThresholdPerHour: 50,
    elevatedFlatFeeUsdc: 3.0,
  },
};
```

File: src/lib/fee.ts (core logic)
```ts
import { PRICING } from '../config/pricing';

export type FeeModel = 'A_counted_exec' | 'B_notcounted_exec' | 'C_charge_upfront' | 'F_flat_exec';

export function computeFee(amountUsdc: number, model: FeeModel, userIsVerified = false, ratePct?: number, flatFeeOverride?: number) {
  const pct = Math.min(ratePct ?? PRICING.percentFeePctDefault, PRICING.maxFeePctCap);
  const flatBase = userIsVerified ? PRICING.flatFeeVerifiedUsdc : PRICING.flatFeeUsdcDefault;
  const flatFee = flatFeeOverride !== undefined ? flatFeeOverride : flatBase;

  let fee = 0;
  if (model === 'F_flat_exec') {
    fee = flatFee;
  } else {
    fee = Math.max(PRICING.minFeeUsdc, amountUsdc * pct);
  }
  // enfore min/max
  if (fee < PRICING.minFeeUsdc) fee = PRICING.minFeeUsdc;
  if (fee > amountUsdc * PRICING.maxFeePctCap) fee = amountUsdc * PRICING.maxFeePctCap;
  return Number(fee.toFixed(6));
}

export function effectiveAmountForCheck(amountUsdc: number, model: FeeModel, fee: number) {
  // B_notcounted_exec and F_flat_exec: fee does not count in invariants
  if (model === 'A_counted_exec') return amountUsdc + fee;
  return amountUsdc;
}
```

Integration points (where to charge)
- Flow (simplified):
  1. Operator creates intent -> simulator evaluates invariants using effectiveAmountForCheck
  2. If verdict = APPROVED:
     a) compute fee via computeFee(...)
     b) perform execution or simulateTransaction
     c) upon success, collect fee: transfer USDC from user -> PDA (or record payable and settle off-chain, depending on custody model)
     d) write ledger entry and emit telemetry
  3. If verdict = FAIL_CLOSED: do not collect fee

- For C_charge_upfront mode (if ever enabled): collect the computed fee at step 1b and store escrow; if fail, refund automatically.

Accounting & settlement
- Prefer on-chain USDC transfer to a platform PDA if custody model allows. Otherwise: collect off-chain via integrated payments (Stripe/fiat) and reconcile in ledger.
- Settlement cadence: daily batching to minimize transaction costs; keep traceability by storing runID and txSignature in ledger entry.

DB Schema (ledger minimal)
- table fee_ledger
  - id (uuid)
  - run_id (string)
  - user_id (string)
  - model (string)
  - rate_pct (decimal)
  - fee_usdc (decimal)
  - flat_fee_usdc (decimal)
  - charged_at (timestamp)
  - refunded (boolean)
  - refund_tx (string)
  - tx_signature (string)
  - verdict (string)

Monitoring & Alerts
- Dashboards (Grafana / Datadog):
  - Fee revenue by model and rate
  - ApprovalRate by cohort and time
  - RefundRate and disputes
  - Attempts per user (top N) to detect abuse
- Alerts:
  - RefundRate > 1% in 24h -> pager
  - ApprovalRate drop > 5% day-over-day -> paging
  - Spike in attempts from single IP/user -> ops

Testing & QA
- Unit tests for computeFee and effectiveAmountForCheck
- Integration tests simulating: APPROVED + success -> fee collected; APPROVED + execute failed (infra) -> refund; FAIL_CLOSED -> no charge
- Staging rollout and A/B tests for rates

Rollout plan
- Canary: internal alpha with percent=0.15%, flat=1.0 USDC for 7 days, monitor logs and KPIs
- Beta: selected users (10% traffic) with A/B testing 0.10% vs 0.15% vs 0.30% for 14 days
- Prod: adopt chosen parameters, enable rate limiting and anti-spam, open dashboard for finance team

Compliance & Legal
- Publish transparent TOS and fee schedule
- Keep audit trail for every fee (ledger + run data) for 7 years
- Engage legal to check jurisdicional constraints on custody and fee collection

Operational playbook (succinct)
- If ApprovalRate drops > 5%: rollback percent fee to previous value and alert product
- If RefundRate > 0.5%: investigate infra/logs; implement hotfix and auto-refund improvements
- If disputes > 0.2% of charges: open account investigation and consider temporary hold

Migration steps (Airtable + DB)
- Create FeeSimulationRuns table in Airtable to store model, runId, amount, fee, verdict, revenue
- Add fee_ledger table in production DB
- Backfill historical runs from administrative_fee_simulation_detailed.csv as needed

---

"Pricing Production Spec" criado e exemplo de implementação em TypeScript prontos em `src/config/pricing.ts` e `src/lib/fee.ts`.
