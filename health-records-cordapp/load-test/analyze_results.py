#!/usr/bin/env python3
"""
Analyze load test results and generate charts
"""

import json
import csv
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import argparse

def load_results(results_dir):
    """Load all test results"""
    summary_files = glob.glob(f"{results_dir}/summary_*.json")
    transaction_files = glob.glob(f"{results_dir}/transactions_*.csv")
    
    results = []
    for summary_file in summary_files:
        with open(summary_file, 'r') as f:
            data = json.load(f)
            data['file'] = summary_file
            results.append(data)
    
    return results, transaction_files


def generate_master_summary(results, output_file):
    """Create master summary table for thesis"""
    if not results:
        print("❌ No results found")
        return
    
    df = pd.DataFrame(results)
    
    # Select key metrics for methodology chapter
    columns = [
        'duration_seconds',
        'total_transactions',
        'failed_transactions',
        'mean_tps',
        'median_tps',
        'avg_latency_ms',
        'median_latency_ms',
        'p95_latency_ms',
        'std_dev_latency_ms',
        'avg_cpu_percent',
        'peak_memory_mb',
        'error_rate_percent'
    ]
    
    summary_df = df[columns].copy()
    
    # Format for better readability
    summary_df['duration_seconds'] = summary_df['duration_seconds'].round(2)
    summary_df['mean_tps'] = summary_df['mean_tps'].round(2)
    summary_df['median_tps'] = summary_df['median_tps'].round(2)
    summary_df['avg_latency_ms'] = summary_df['avg_latency_ms'].round(2)
    summary_df['median_latency_ms'] = summary_df['median_latency_ms'].round(2)
    summary_df['p95_latency_ms'] = summary_df['p95_latency_ms'].round(2)
    summary_df['std_dev_latency_ms'] = summary_df['std_dev_latency_ms'].round(2)
    summary_df['avg_cpu_percent'] = summary_df['avg_cpu_percent'].round(2)
    summary_df['peak_memory_mb'] = summary_df['peak_memory_mb'].round(2)
    summary_df['error_rate_percent'] = summary_df['error_rate_percent'].round(2)
    
    # Save to CSV
    summary_df.to_csv(output_file, index=False)
    print(f"💾 Master summary saved: {output_file}")
    
    # Display formatted table
    print("\n" + "="*100)
    print("📊 MASTER SUMMARY TABLE - FOR METHODOLOGY CHAPTER")
    print("="*100)
    print(summary_df.to_string(index=False))
    print("="*100)
    
    return summary_df


def plot_latency_distribution(transaction_files, output_dir):
    """Generate latency distribution charts"""
    os.makedirs(output_dir, exist_ok=True)
    
    for tx_file in transaction_files:
        df = pd.read_csv(tx_file)
        successful = df[df['success'] == True]
        
        if len(successful) < 10:
            continue
        
        latencies_ms = successful['latency'] * 1000
        
        plt.figure(figsize=(15, 6))
        
        # Histogram
        plt.subplot(1, 2, 1)
        plt.hist(latencies_ms, bins=50, edgecolor='black', alpha=0.7)
        plt.xlabel('Latency (ms)')
        plt.ylabel('Frequency')
        plt.title('Latency Distribution Histogram')
        plt.grid(True, alpha=0.3)
        
        # Box plot
        plt.subplot(1, 2, 2)
        plt.boxplot(latencies_ms, vert=True)
        plt.ylabel('Latency (ms)')
        plt.title('Latency Box Plot')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        timestamp = os.path.basename(tx_file).replace('transactions_', '').replace('.csv', '')
        output_file = f"{output_dir}/latency_distribution_{timestamp}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Latency chart saved: {output_file}")


def plot_tps_over_time(transaction_files, output_dir):
    """Generate TPS over time chart"""
    os.makedirs(output_dir, exist_ok=True)
    
    for tx_file in transaction_files:
        df = pd.read_csv(tx_file)
        successful = df[df['success'] == True]
        
        if len(successful) < 10:
            continue
        
        # Calculate TPS in 1-second windows
        start_time = successful['timestamp'].min()
        tps_data = []
        window_start = start_time
        
        while window_start < successful['timestamp'].max():
            window_end = window_start + 1.0
            window_txs = successful[
                (successful['timestamp'] >= window_start) & 
                (successful['timestamp'] < window_end)
            ]
            tps_data.append({
                'time': window_start - start_time,
                'tps': len(window_txs)
            })
            window_start = window_end
        
        tps_df = pd.DataFrame(tps_data)
        
        plt.figure(figsize=(14, 6))
        plt.plot(tps_df['time'], tps_df['tps'], linewidth=2, label='TPS')
        
        # Add sustained rate indicator (plateau)
        mean_tps = tps_df['tps'].mean()
        plateau_start = tps_df[tps_df['tps'] >= mean_tps * 0.9]['time'].min()
        
        if not pd.isna(plateau_start):
            plt.axvline(x=plateau_start, color='g', linestyle='--', alpha=0.7, label=f'Plateau start: {plateau_start:.1f}s')
        
        plt.axhline(y=mean_tps, color='r', linestyle='--', alpha=0.7, label=f'Mean: {mean_tps:.2f} TPS')
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Transactions Per Second')
        plt.title('TPS Over Time (Sustained Rate Analysis)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        timestamp = os.path.basename(tx_file).replace('transactions_', '').replace('.csv', '')
        output_file = f"{output_dir}/tps_over_time_{timestamp}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 TPS chart saved: {output_file}")


def plot_latency_vs_tps(transaction_files, output_dir):
    """Generate latency vs TPS correlation chart"""
    os.makedirs(output_dir, exist_ok=True)
    
    for tx_file in transaction_files:
        df = pd.read_csv(tx_file)
        successful = df[df['success'] == True]
        
        if len(successful) < 10:
            continue
        
        # Calculate rolling metrics
        successful = successful.sort_values('timestamp')
        successful['latency_ms'] = successful['latency'] * 1000
        
        # TPS in windows
        start_time = successful['timestamp'].min()
        successful['time_window'] = ((successful['timestamp'] - start_time) // 1.0).astype(int)
        tps_by_window = successful.groupby('time_window').size()
        successful['tps'] = successful['time_window'].map(tps_by_window)
        
        # Identify saturation point (where latency spikes)
        plt.figure(figsize=(12, 6))
        scatter = plt.scatter(successful['tps'], successful['latency_ms'], 
                            c=successful['timestamp'] - start_time, 
                            cmap='viridis', alpha=0.6, s=20)
        
        plt.colorbar(scatter, label='Time (seconds)')
        plt.xlabel('TPS (in 1-second window)')
        plt.ylabel('Latency (ms)')
        plt.title('Latency vs TPS Correlation (Saturation Analysis)')
        plt.grid(True, alpha=0.3)
        
        timestamp = os.path.basename(tx_file).replace('transactions_', '').replace('.csv', '')
        output_file = f"{output_dir}/latency_vs_tps_{timestamp}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Correlation chart saved: {output_file}")


def generate_error_analysis(results_dir, output_file):
    """Generate error categorization report"""
    error_files = glob.glob(f"{results_dir}/errors_*.csv")
    
    if not error_files:
        print("⚠️  No error files found")
        return
    
    all_errors = []
    for error_file in error_files:
        try:
            df = pd.read_csv(error_file)
            all_errors.append(df)
        except:
            continue
    
    if not all_errors:
        return
    
    errors_df = pd.concat(all_errors, ignore_index=True)
    error_summary = errors_df.groupby('error').size().reset_index(name='count')
    error_summary = error_summary.sort_values('count', ascending=False)
    
    error_summary.to_csv(output_file, index=False)
    print(f"📊 Error analysis saved: {output_file}")
    
    # Display
    print("\n" + "="*80)
    print("⚠️  ERROR CATEGORIZATION")
    print("="*80)
    print(error_summary.to_string(index=False))
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description='Analyze load test results')
    parser.add_argument('--results-dir', default='results', help='Results directory')
    parser.add_argument('--output-dir', default='analysis', help='Output directory')
    
    args = parser.parse_args()
    
    print(f"📂 Loading results from: {args.results_dir}")
    results, transaction_files = load_results(args.results_dir)
    
    if not results:
        print("❌ No results found")
        sys.exit(1)
    
    print(f"✅ Found {len(results)} test runs")
    
    # Generate master summary
    print("\n📊 Generating master summary...")
    generate_master_summary(results, f"{args.output_dir}/master_summary.csv")
    
    # Generate charts
    print("\n📊 Generating charts...")
    plot_latency_distribution(transaction_files, args.output_dir)
    plot_tps_over_time(transaction_files, args.output_dir)
    plot_latency_vs_tps(transaction_files, args.output_dir)
    
    # Error analysis
    print("\n📊 Generating error analysis...")
    generate_error_analysis(args.results_dir, f"{args.output_dir}/error_analysis.csv")
    
    print("\n✅ Analysis complete!")
    print(f"📂 Results in: {args.output_dir}/")


if __name__ == '__main__':
    import sys
    main()