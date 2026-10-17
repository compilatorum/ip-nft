#!/usr/bin/env python3
"""
simulate_embornal.py

Monte-Carlo simulator adapted for the ProofGate Embornal B2C use-case (Embornal Cibereconomico Autoregenerativo).

Features:
- Start AUM default 15,000 USDC
- Monthly DCA (configurable)
- Basket of ReFi/Phygital assets with per-asset mean monthly returns and volatility
- Regenerative Wealth Index (RWI) computed each month as a function of portfolio performance and an exogenous "eco_health" index
- Shock event at configurable month (default month 7) that applies a drawdown to some assets
- Autoregeneration: after shock, allocation rebalances towards resilient assets over a recovery window
- Integrates fee models (AUM fee, deposit fee, performance fee) optionally using parameters from pricing

Outputs:
- summary CSV per simulation run: proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_summary.csv
- sample monthly timeseries for first few sims: proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_detail_sample.csv

Usage:
  pip install pandas numpy
  python proofgate-simulator-spreadsheet/simulate_embornal.py --n-sims 5000 --months 12 --out-dir proofgate-simulator-spreadsheet/embornal/out

"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import math


def compute_rwi(portfolio_returns, eco_health, weights=None):
    """
    Compute a Regenerative Wealth Index (RWI) combining financial returns and ecological health.
    Simple formulation (example): RWI = geometric_mean(1 + portfolio_return) * eco_health_factor
    where eco_health_factor in [0,2], 1==neutral.
    """
    if weights is None:
        weights = np.ones(len(portfolio_returns)) / len(portfolio_returns)
    # portfolio return = weighted sum of component returns
    port_ret = np.dot(weights, portfolio_returns)
    # geometric component (accumulated factor)
    rwi = (1.0 + port_ret) * eco_health
    return rwi


def simulate_one_run(
    start_aum=15000.0,
    monthly_deposit=500.0,
    months=12,
    asset_specs=None,
    eco_health_init=1.0,
    eco_health_vol=0.02,
    shock_month=7,
    shock_severity_mean=0.25,
    shock_severity_std=0.10,
    regen_strength=0.5,
    aum_fee_ann_pct=0.0015,  # 0.15% default
    deposit_fee=1.0,
    perf_fee_pct=15.0,
    hurdle_ann_pct=0.0,
    seed=None,
):
    rng = np.random.default_rng(seed)

    # asset_specs: list of dicts with 'name', 'mu_month', 'sigma_month', 'resilience'
    if asset_specs is None:
        asset_specs = [
            {'name': 'ReFiTokenA', 'mu_month': 0.01, 'sigma_month': 0.05, 'resilience': 0.9},
            {'name': 'PhygitalAssetB', 'mu_month': 0.008, 'sigma_month': 0.04, 'resilience': 0.85},
            {'name': 'GreenBondC', 'mu_month': 0.002, 'sigma_month': 0.01, 'resilience': 0.98},
            {'name': 'ImpactLP', 'mu_month': 0.015, 'sigma_month': 0.08, 'resilience': 0.7},
            {'name': 'OracularPDA', 'mu_month': 0.005, 'sigma_month': 0.03, 'resilience': 0.95},
        ]

    n_assets = len(asset_specs)
    weights = np.array([1.0 / n_assets] * n_assets)

    aum = start_aum
    hwm = start_aum

    total_deposit_fees = 0.0
    total_aum_fee = 0.0
    total_perf_fee = 0.0
    eco_health = eco_health_init

    monthly_records = []

    for m in range(1, months + 1):
        # deposit
        aum += monthly_deposit
        total_deposit_fees += deposit_fee

        # sample per-asset returns
        asset_returns = np.array([
            rng.normal(spec['mu_month'], spec['sigma_month']) for spec in asset_specs
        ])

        # shock event
        if m == shock_month:
            severity = max(0.0, rng.normal(shock_severity_mean, shock_severity_std))
            # apply negative shock to some assets scaled by (1 - resilience)
            shock_factors = np.array([-(severity * (1.0 - spec['resilience'])) for spec in asset_specs])
            asset_returns = asset_returns + shock_factors
            # eco health also drops
            eco_health *= max(0.3, 1.0 - severity * 0.5)
       
        # after shock: autoregeneration (rebalance towards high-resilience assets)
        if m > shock_month and regen_strength > 0:
            # increase weight proportionally to resilience
            resil = np.array([spec['resilience'] for spec in asset_specs])
            resil_weights = resil / resil.sum()
            weights = (1 - regen_strength) * weights + regen_strength * resil_weights
            weights = weights / weights.sum()

            # eco health recovers partially
            eco_health = min(1.0 + 0.02 * (m - shock_month), eco_health_init * 1.2)

        # portfolio return
        port_ret = float(np.dot(weights, asset_returns))

        # AUM fee (monthly pro rata)
        aum_fee_month = (aum_fee_ann_pct) / 12.0 * aum
        total_aum_fee += aum_fee_month
        aum = aum * (1.0 + port_ret) - aum_fee_month

        # Performance fee eligibility using HWM + hurdle (simple monthly approximation)
        hurdle_month = (1 + hurdle_ann_pct / 100.0) ** (1 / 12.0) - 1
        hurdle_level = hwm * (1.0 + hurdle_month)
        eligible_gain = max(0.0, aum - max(hwm, hurdle_level))
        perf_fee_month = 0.0
        if eligible_gain > 0:
            perf_fee_month = (perf_fee_pct / 100.0) * eligible_gain
            total_perf_fee += perf_fee_month
            aum -= perf_fee_month
            hwm = aum

        # compute RWI
        rwi = compute_rwi(asset_returns, eco_health, weights)

        monthly_records.append({
            'month': m,
            'aum_end': aum,
            'port_return': port_ret,
            'aum_fee_month': aum_fee_month,
            'perf_fee_month': perf_fee_month,
            'deposit_fee_this_month': deposit_fee,
            'eco_health': eco_health,
            'rwi': rwi,
            'weights': weights.copy(),
        })

    return {
        'end_aum': aum,
        'total_deposits': monthly_deposit * months,
        'profit': aum - start_aum - monthly_deposit * months,
        'total_aum_fee': total_aum_fee,
        'total_deposit_fees': total_deposit_fees,
        'total_perf_fee': total_perf_fee,
        'monthly_records': monthly_records,
    }


def run_simulations(n_sims=2000, months=12, out_dir='proofgate-simulator-spreadsheet/embornal/out', seed_base=42):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    summaries = []
    details = []

    for sim in range(n_sims):
        res = simulate_one_run(months=months, seed=seed_base + sim)
        summaries.append({
            'sim': sim,
            'end_aum': res['end_aum'],
            'total_deposits': res['total_deposits'],
            'profit': res['profit'],
            'total_aum_fee': res['total_aum_fee'],
            'total_deposit_fees': res['total_deposit_fees'],
            'total_perf_fee': res['total_perf_fee'],
        })
        if sim < min(5, n_sims):
            for mr in res['monthly_records']:
                row = {'sim': sim, **{k: v for k, v in mr.items() if k != 'weights'}}
                # weights to separate columns
                weights = mr['weights']
                for i, w in enumerate(weights):
                    row[f'w_{i}'] = w
                details.append(row)

    pd.DataFrame(summaries).to_csv(out / 'embornal_simulation_summary.csv', index=False)
    pd.DataFrame(details).to_csv(out / 'embornal_simulation_detail_sample.csv', index=False)
    print(f'Wrote {out}/embornal_simulation_summary.csv and detail sample')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-sims', type=int, default=2000)
    parser.add_argument('--months', type=int, default=12)
    parser.add_argument('--out-dir', type=str, default='proofgate-simulator-spreadsheet/embornal/out')
    args = parser.parse_args()

    run_simulations(n_sims=args.n_sims, months=args.months, out_dir=args.out_dir)


if __name__ == '__main__':
    main()
