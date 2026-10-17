#!/usr/bin/env python3
"""embornal_analyze.py

Analyze outputs from simulate_embornal.py and generate charts/summary stats.
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def analyze(summary_csv: Path, detail_csv: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(summary_csv)
    detail = pd.read_csv(detail_csv)

    stats = df.agg({'end_aum': ['mean','median','std'], 'profit': ['mean','median','std'], 'total_perf_fee': ['mean','sum']}).T
    stats.to_csv(out_dir / 'embornal_summary_stats.csv')

    # profit histogram
    plt.figure(figsize=(8,4))
    plt.hist(df['profit'], bins=80)
    plt.title('Profit distribution — Embornal simulations')
    plt.xlabel('Profit (USDC)')
    plt.ylabel('Frequency')
    plt.savefig(out_dir / 'profit_histogram.png', dpi=200)
    plt.close()

    # boxplot of RWI by month using detail sample
    if 'rwi' in detail.columns:
        detail.boxplot(column='rwi', by='month', figsize=(10,4))
        plt.title('RWI distribution by month (sample sims)')
        plt.suptitle('')
        plt.xlabel('Month')
        plt.ylabel('RWI')
        plt.savefig(out_dir / 'rwi_boxplot_by_month.png', dpi=200)
        plt.close()

    print('Analysis written to', out_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', type=str, default='proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_summary.csv')
    parser.add_argument('--detail', type=str, default='proofgate-simulator-spreadsheet/embornal/out/embornal_simulation_detail_sample.csv')
    parser.add_argument('--out-dir', type=str, default='proofgate-simulator-spreadsheet/embornal/out')
    args = parser.parse_args()
    analyze(Path(args.summary), Path(args.detail), Path(args.out_dir))

if __name__ == '__main__':
    main()
