#!/usr/bin/env python3
"""simulate_fee_models.py

Monte Carlo + sensitivity sweep for fee models.

Modelos cobertos:
- A_counted_exec: taxa conta no limite do trade
- B_notcounted_exec: taxa não conta no limite do trade
- C_charge_upfront: taxa cobrada antes da avaliação e em falha
- F_flat_exec: taxa fixa por execução

Uso:
  pip install pandas numpy matplotlib
  python simulate_fee_models.py --n-runs 5000 --output-dir proofgate-simulator-spreadsheet/out
"""

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / 'out'

@dataclass
class FeeScenario:
    model: str
    rate_pct: float
    flat_fee: float = 0.0


models = [
    'A_counted_exec',
    'B_notcounted_exec',
    'C_charge_upfront',
    'F_flat_exec',
]


def compute_fee(amount: float, model: str, rate_pct: float, flat_fee: float) -> float:
    if model == 'F_flat_exec':
        return flat_fee
    if model == 'A_counted_exec':
        return amount * rate_pct / 100.0
    if model == 'B_notcounted_exec':
        return amount * rate_pct / 100.0
    if model == 'C_charge_upfront':
        return amount * rate_pct / 100.0
    raise ValueError(f'Unknown model: {model}')


def verdict_for_run(amount: float, cumulative_daily: float, oracle_age: float, confidence_bps: float,
                   divergence_bps: float, slippage_bps: float, mandate: Dict[str, float],
                   model: str, rate_pct: float, flat_fee: float) -> Dict[str, Any]:
    """Return verdict and fee information for one hypothetical run.

    The same invariant thresholds as the ProofGate spec are used:
      C1 asset allowed
      C2 volume cap
      C3 oracle freshness
      C4 confidence threshold
      C5 divergence threshold
      C6 slippage threshold
    """
    effective_amount = amount
    fee = compute_fee(amount, model, rate_pct, flat_fee)

    if model == 'A_counted_exec':
        effective_amount = amount + fee
    elif model == 'C_charge_upfront':
        # fee is charged at attempt time; it does not change the verdict in this simplified model
        effective_amount = amount
    elif model == 'F_flat_exec':
        effective_amount = amount

    # Mandate inputs (tunable)
    allowed_mints = mandate.get('allowed_mints', ['AAPLx', 'USDC', 'SOL', 'BONK'])
    target_mint = mandate.get('target_mint', 'AAPLx')
    max_trade = mandate.get('max_trade_amount_usdc', 250.0)
    max_daily = mandate.get('max_daily_volume_usdc', 1000.0)
    max_oracle_age = mandate.get('max_oracle_age_seconds', 300.0)
    max_confidence_bps = mandate.get('max_confidence_bps', 1000.0)
    max_divergence_bps = mandate.get('max_divergence_bps', 2000.0)
    max_slippage_bps = mandate.get('max_slippage_bps', 1000.0)

    c1 = target_mint in allowed_mints
    c2 = (effective_amount <= max_trade) and ((effective_amount + cumulative_daily) <= max_daily)
    c3 = oracle_age <= max_oracle_age
    c4 = confidence_bps <= max_confidence_bps
    c5 = divergence_bps <= max_divergence_bps
    c6 = slippage_bps <= max_slippage_bps

    verdict = 'APPROVED' if all([c1, c2, c3, c4, c5, c6]) else 'FAIL_CLOSED'
    revenue = fee if verdict == 'APPROVED' and model in ('B_notcounted_exec', 'F_flat_exec') else fee if model == 'C_charge_upfront' else 0.0

    return {
        'fee': fee,
        'effective_amount': effective_amount,
        'revenue': revenue,
        'verdict': verdict,
        'c1': c1,
        'c2': c2,
        'c3': c3,
        'c4': c4,
        'c5': c5,
        'c6': c6,
    }


def build_mandate() -> Dict[str, Any]:
    return {
        'allowed_mints': ['AAPLx', 'USDC', 'SOL', 'BONK'],
        'target_mint': 'AAPLx',
        'max_trade_amount_usdc': 250.0,
        'max_daily_volume_usdc': 1000.0,
        'max_oracle_age_seconds': 300.0,
        'max_confidence_bps': 1000.0,
        'max_divergence_bps': 2000.0,
        'max_slippage_bps': 1000.0,
    }


def simulate_model(model: str, rate_pct: float, flat_fee: float, n_runs: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    mandate = build_mandate()

    amounts = rng.uniform(50, 250, size=n_runs)
    cumulative_daily = rng.uniform(0, 350, size=n_runs)
    oracle_age = rng.uniform(5, 450, size=n_runs)
    confidence_bps = rng.uniform(10, 2500, size=n_runs)
    divergence_bps = rng.uniform(50, 5000, size=n_runs)
    slippage_bps = rng.uniform(10, 2200, size=n_runs)

    rows = []
    for i in range(n_runs):
        result = verdict_for_run(
            amount=amounts[i],
            cumulative_daily=cumulative_daily[i],
            oracle_age=oracle_age[i],
            confidence_bps=confidence_bps[i],
            divergence_bps=divergence_bps[i],
            slippage_bps=slippage_bps[i],
            mandate=mandate,
            model=model,
            rate_pct=rate_pct,
            flat_fee=flat_fee,
        )
        rows.append({
            'Model': model,
            'RatePct': rate_pct,
            'FlatFee': flat_fee,
            'RunID': f'{model}_{i:04d}',
            'Amount': round(float(amounts[i]), 2),
            'FeeAmount': round(float(result['fee']), 2),
            'EffectiveTradeAmount': round(float(result['effective_amount']), 2),
            'PassAfter': result['verdict'] == 'APPROVED',
            'VerdictBefore': 'APPROVED',
            'VerdictAfter': result['verdict'],
            'RevenueCollected': round(float(result['revenue']), 2),
        })

    return pd.DataFrame(rows)


def aggregate_results(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(['Model', 'RatePct', 'FlatFee'], as_index=False).agg(
        Attempts=('RunID', 'count'),
        ApprovedBefore=('VerdictBefore', lambda s: (s == 'APPROVED').sum()),
        ApprovedAfter=('VerdictAfter', lambda s: (s == 'APPROVED').sum()),
        ApprovalsLost=('PassAfter', lambda s: (s == False).sum()),
        TotalRevenue=('RevenueCollected', 'sum'),
        AvgRevenuePerApproved=('RevenueCollected', 'mean'),
    )
    summary['ApprovalRateBefore'] = summary['ApprovedBefore'] / summary['Attempts']
    summary['ApprovalRateAfter'] = summary['ApprovedAfter'] / summary['Attempts']
    summary['ApprovalsLost'] = summary['ApprovedBefore'] - summary['ApprovedAfter']
    return summary


def sweep_models(n_runs: int) -> pd.DataFrame:
    scenarios = []
    # rate sweep, flat fee sweep
    rate_values = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    flat_values = [0.0, 1.0, 5.0, 10.0]
    for model in models:
        for rate in rate_values:
            if model == 'F_flat_exec':
                flat_fee = 1.0
            else:
                flat_fee = 0.0
            scenarios.append(FeeScenario(model=model, rate_pct=rate, flat_fee=flat_fee))
        if model == 'F_flat_exec':
            for flat_fee in flat_values[1:]:
                scenarios.append(FeeScenario(model=model, rate_pct=0.0, flat_fee=flat_fee))
    frames = []
    for scenario in scenarios:
        frames.append(simulate_model(scenario.model, scenario.rate_pct, scenario.flat_fee, n_runs=n_runs, seed=42 + len(frames)))
    combined = pd.concat(frames, ignore_index=True)
    return aggregate_results(combined)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-runs', type=int, default=5000)
    parser.add_argument('--output-dir', type=str, default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = sweep_models(args.n_runs)
    summary_path = out_dir / 'administrative_fee_simulation_aggregated.csv'
    summary.to_csv(summary_path, index=False)

    # Save a sample detailed CSV for traceability as well.
    sample = simulate_model('B_notcounted_exec', rate_pct=0.5, flat_fee=0.0, n_runs=200, seed=7)
    sample.to_csv(out_dir / 'administrative_fee_simulation_detail_sample.csv', index=False)

    print(f'Wrote aggregated summary to {summary_path}')
    print(summary[['Model', 'RatePct', 'ApprovedAfter', 'ApprovalRateAfter', 'TotalRevenue']].sort_values('Model').head(30).to_string(index=False))


if __name__ == '__main__':
    main()
