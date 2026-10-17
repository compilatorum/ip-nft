#!/usr/bin/env python3
"""simulate_pricing_options.py

Simula e compara 3 modelos de pricing:
- AUM fee (percentual recorrente sobre saldo)
- Deposit fee (taxa fixa por depósito)
- Performance fee (percentual sobre rendimento)

Gera um CSV com resultados agregados para cenários predefinidos.

Uso:
  python simulate_pricing_options.py --out proofgate-simulator-spreadsheet/pricing_models_simulation_results.csv
"""

import argparse
from math import pow
from pathlib import Path
import csv

SCENARIOS = [
    {
        'name': 'Conservative',
        'start_aum': 100000.0,
        'monthly_deposit': 1000.0,
        'monthly_return_pct': 0.2,  # percent -> 0.2% = 0.2
        'months': 12,
    },
    {
        'name': 'Balanced',
        'start_aum': 500000.0,
        'monthly_deposit': 5000.0,
        'monthly_return_pct': 0.8,
        'months': 12,
    },
    {
        'name': 'Aggressive',
        'start_aum': 200000.0,
        'monthly_deposit': 10000.0,
        'monthly_return_pct': 2.0,
        'months': 12,
    },
]

# Fee params (defaults)
AUM_FEE_ANNUAL_PCT = 0.25  # 0.25% annual
DEPOSIT_FEE_PER_DEPOSIT = 1.0  # USDC per deposit
PERFORMANCE_FEE_PCT = 20.0  # 20% of profits


def simulate_scenario(s, aum_fee_ann_pct=AUM_FEE_ANNUAL_PCT, deposit_fee=DEPOSIT_FEE_PER_DEPOSIT, perf_fee_pct=PERFORMANCE_FEE_PCT):
    S = s['start_aum']
    d = s['monthly_deposit']
    r_pct = s['monthly_return_pct']
    r = r_pct / 100.0
    n = s['months']

    growth = pow(1 + r, n)
    end_aum = S * growth + d * ((growth - 1) / r)
    total_deposits = d * n
    profit = end_aum - S - total_deposits
    avg_aum = (S + end_aum) / 2.0

    # AUM fee revenue (annualized on average AUM)
    aum_fee_revenue = (aum_fee_ann_pct / 100.0) * avg_aum

    # Deposit fee revenue
    num_deposits = n  # monthly deposit model
    deposit_fee_revenue = deposit_fee * num_deposits

    # Performance fee revenue (on profits only)
    perf_fee_revenue = perf_fee_pct / 100.0 * profit if profit > 0 else 0.0

    return {
        'Scenario': s['name'],
        'StartAUM': round(S,2),
        'MonthlyDeposit': round(d,2),
        'MonthlyReturnPct': r_pct,
        'Months': n,
        'EndAUM': round(end_aum,2),
        'TotalDeposits': round(total_deposits,2),
        'Profit': round(profit,2),
        'AvgAUM': round(avg_aum,2),
        'AUMFeeAnnualPct': aum_fee_ann_pct,
        'AUMFeeRevenue': round(aum_fee_revenue,2),
        'DepositFeePerDeposit': deposit_fee,
        'NumDeposits': num_deposits,
        'DepositFeeRevenue': round(deposit_fee_revenue,2),
        'PerfFeePct': perf_fee_pct,
        'PerformanceFeeRevenue': round(perf_fee_revenue,2),
    }


def write_csv(rows, path: Path):
    fieldnames = list(rows[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, default='proofgate-simulator-spreadsheet/pricing_models_simulation_results.csv')
    args = parser.parse_args()

    rows = []
    for s in SCENARIOS:
        rows.append(simulate_scenario(s))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out)
    print(f'Wrote {out}')

if __name__ == '__main__':
    main()
