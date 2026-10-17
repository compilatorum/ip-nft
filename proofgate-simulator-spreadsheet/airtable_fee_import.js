#!/usr/bin/env python3
"""generate_fee_charts.py

Reads the aggregated CSV and produces chart PNGs.

Usage:
  pip install pandas matplotlib
  python generate_fee_charts.py --csv proofgate-simulator-spreadsheet/administrative_fee_simulation_aggregated.csv --out-dir proofgate-simulator-spreadsheet/charts
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


def plot_model_comparison(csv_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    # create aggregate revenue chart by model / rate
    for model in sorted(df['Model'].unique()):
        sub = df[df['Model'] == model].copy()
        plt.figure(figsize=(9, 5))
        plt.plot(sub['RatePct'].astype(float), sub['TotalRevenue'].astype(float), marker='o', linewidth=2)
        plt.title(f'{model} — Revenue vs Rate')
        plt.xlabel('Rate %')
        plt.ylabel('Total Revenue')
        plt.grid(alpha=0.2)
        plt.tight_layout()
        plt.savefig(out_dir / f'{model}_revenue_vs_rate.png', dpi=200)
        plt.close()

        plt.figure(figsize=(9, 5))
        plt.plot(sub['RatePct'].astype(float), sub['ApprovalRateAfter'].astype(float), marker='o', linewidth=2)
        plt.title(f'{model} — Approval Rate vs Rate')
        plt.xlabel('Rate %')
        plt.ylabel('Approval Rate')
        plt.grid(alpha=0.2)
        plt.tight_layout()
        plt.savefig(out_dir / f'{model}_approval_vs_rate.png', dpi=200)
        plt.close()

    # compare models at common rate
    common_rates = sorted(df['RatePct'].dropna().unique())
    for rate in common_rates[:5]:
        sample = df[df['RatePct'] == rate].copy()
        plt.figure(figsize=(9, 5))
        plt.bar(sample['Model'], sample['TotalRevenue'], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        plt.title(f'Revenue by Model at {rate}%')
        plt.ylabel('Total Revenue')
        plt.xticks(rotation=25)
        plt.tight_layout()
        plt.savefig(out_dir / f'revenue_by_model_at_{rate}.png', dpi=200)
        plt.close()

    print(f'Wrote charts to {out_dir}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=str, default='proofgate-simulator-spreadsheet/administrative_fee_simulation_aggregated.csv')
    parser.add_argument('--out-dir', type=str, default='proofgate-simulator-spreadsheet/charts')
    args = parser.parse_args()
    plot_model_comparison(Path(args.csv), Path(args.out_dir))


if __name__ == '__main__':
    main()

