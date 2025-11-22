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
import numpy as np
import sys

def load_results(results_dir):
    """Load all test results"""
    summary_files = sorted(glob.glob(f"{results_dir}/summary_*.json"))
    transaction_files = sorted(glob.glob(f"{results_dir}/transactions_*.csv"))
    system_files = sorted(glob.glob(f"{results_dir}/system_*.csv"))
    
    results = []
    for summary_file in summary_files:
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
                data['file'] = summary_file
                results.append(data)
        except Exception as e:
            print(f"⚠️  Warning: Could not load {summary_file}: {e}")
    
    return results, transaction_files, system_files

def generate_master_summary(results, output_dir):
    """Create master summary table for thesis"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    if not results:
        print("❌ No results found")
        return None
    
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
    
    # Filter columns that exist
    available_cols = [col for col in columns if col in df.columns]
    summary_df = df[available_cols].copy()
    
    # Format for better readability
    numeric_cols = summary_df.select_dtypes(include=[np.number]).columns
    summary_df[numeric_cols] = summary_df[numeric_cols].round(2)
    
    # Save to CSV
    output_file = f"{output_dir}/master_summary.csv"
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
        try:
            df = pd.read_csv(tx_file)
            successful = df[df['success'] == True]
            
            if len(successful) < 10:
                print(f"⚠️  Skipping {tx_file}: Not enough successful transactions")
                continue
            
            latencies_ms = successful['latency'] * 1000
            
            plt.figure(figsize=(15, 6))
            
            # Histogram
            plt.subplot(1, 2, 1)
            plt.hist(latencies_ms, bins=50, edgecolor='black', alpha=0.7, color='blue')
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
        except Exception as e:
            print(f"⚠️  Error processing {tx_file}: {e}")

def plot_tps_over_time(transaction_files, output_dir):
    """Generate TPS over time chart"""
    os.makedirs(output_dir, exist_ok=True)
    
    for tx_file in transaction_files:
        try:
            df = pd.read_csv(tx_file)
            successful = df[df['success'] == True]
            
            if len(successful) < 10:
                print(f"⚠️  Skipping {tx_file}: Not enough successful transactions")
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
            plt.plot(tps_df['time'], tps_df['tps'], linewidth=2, label='TPS', color='green')
            
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
        except Exception as e:
            print(f"⚠️  Error processing {tx_file}: {e}")

def plot_latency_vs_tps(transaction_files, output_dir):
    """Generate latency vs TPS correlation chart"""
    os.makedirs(output_dir, exist_ok=True)
    
    for tx_file in transaction_files:
        try:
            df = pd.read_csv(tx_file)
            successful = df[df['success'] == True]
            
            if len(successful) < 10:
                print(f"⚠️  Skipping {tx_file}: Not enough successful transactions")
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
        except Exception as e:
            print(f"⚠️  Error processing {tx_file}: {e}")

def plot_system_resources_over_time(system_files, output_dir):
    """Generate CPU and Memory usage over time charts"""
    os.makedirs(output_dir, exist_ok=True)
    
    for system_file in system_files:
        try:
            df = pd.read_csv(system_file)
            
            if len(df) < 5:
                print(f"⚠️  Skipping {system_file}: Not enough samples")
                continue
            
            # Normalize time to start at 0
            df['time_seconds'] = df['timestamp'] - df['timestamp'].min()
            
            plt.figure(figsize=(15, 10))
            
            # CPU Usage subplot
            plt.subplot(2, 1, 1)
            plt.plot(df['time_seconds'], df['cpu_percent'], linewidth=2, color='orange', label='CPU %')
            plt.fill_between(df['time_seconds'], df['cpu_percent'], alpha=0.3, color='orange')
            plt.axhline(y=df['cpu_percent'].mean(), color='r', linestyle='--', alpha=0.7, 
                       label=f'Average: {df["cpu_percent"].mean():.2f}%')
            plt.xlabel('Time (seconds)')
            plt.ylabel('CPU Usage (%)')
            plt.title('CPU Usage Over Time During Load Test')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Memory Usage subplot
            plt.subplot(2, 1, 2)
            plt.plot(df['time_seconds'], df['memory_mb'], linewidth=2, color='purple', label='Memory MB')
            plt.fill_between(df['time_seconds'], df['memory_mb'], alpha=0.3, color='purple')
            plt.axhline(y=df['memory_mb'].mean(), color='r', linestyle='--', alpha=0.7,
                       label=f'Average: {df["memory_mb"].mean():.2f} MB')
            plt.axhline(y=df['memory_mb'].max(), color='g', linestyle='--', alpha=0.7,
                       label=f'Peak: {df["memory_mb"].max():.2f} MB')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Memory Usage (MB)')
            plt.title('Memory Usage Over Time During Load Test')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            timestamp = os.path.basename(system_file).replace('system_', '').replace('.csv', '')
            output_file = f"{output_dir}/system_resources_{timestamp}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 System resources chart saved: {output_file}")
        except Exception as e:
            print(f"⚠️  Error processing {system_file}: {e}")

def plot_system_vs_tps(transaction_files, system_files, output_dir):
    """Generate CPU/Memory vs TPS correlation charts"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Match transaction and system files by timestamp
    tx_files_by_ts = {f.split('_')[-1].replace('.csv', ''): f for f in transaction_files}
    sys_files_by_ts = {f.split('_')[-1].replace('.csv', ''): f for f in system_files}
    
    common_timestamps = set(tx_files_by_ts.keys()) & set(sys_files_by_ts.keys())
    
    for ts in common_timestamps:
        try:
            tx_file = tx_files_by_ts[ts]
            sys_file = sys_files_by_ts[ts]
            
            tx_df = pd.read_csv(tx_file)
            sys_df = pd.read_csv(sys_file)
            
            successful = tx_df[tx_df['success'] == True]
            
            if len(successful) < 10 or len(sys_df) < 5:
                print(f"⚠️  Skipping correlation for {ts}: Insufficient data")
                continue
            
            # Calculate TPS per window
            start_time = successful['timestamp'].min()
            successful['time_window'] = ((successful['timestamp'] - start_time) // 1.0).astype(int)
            tps_by_window = successful.groupby('time_window').size().reset_index(name='tps')
            tps_by_window['time_window'] = tps_by_window['time_window'].astype(int)
            
            # Align system metrics to same windows
            sys_df['time_window'] = ((sys_df['timestamp'] - start_time) // 1.0).astype(int)
            sys_avg_by_window = sys_df.groupby('time_window')[['cpu_percent', 'memory_mb']].mean().reset_index()
            sys_avg_by_window['time_window'] = sys_avg_by_window['time_window'].astype(int)
            
            # Merge data
            merged = pd.merge(tps_by_window, sys_avg_by_window, on='time_window', how='inner')
            
            if len(merged) < 5:
                print(f"⚠️  Skipping correlation for {ts}: Insufficient merged data")
                continue
            
            plt.figure(figsize=(15, 6))
            
            # CPU vs TPS
            plt.subplot(1, 2, 1)
            plt.scatter(merged['tps'], merged['cpu_percent'], alpha=0.7, s=30, color='orange')
            plt.xlabel('Transactions Per Second')
            plt.ylabel('CPU Usage (%)')
            plt.title('CPU Usage vs TPS Correlation')
            plt.grid(True, alpha=0.3)
            
            # Add correlation coefficient
            corr = merged['tps'].corr(merged['cpu_percent'])
            plt.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=plt.gca().transAxes, 
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
            
            # Memory vs TPS
            plt.subplot(1, 2, 2)
            plt.scatter(merged['tps'], merged['memory_mb'], alpha=0.7, s=30, color='purple')
            plt.xlabel('Transactions Per Second')
            plt.ylabel('Memory Usage (MB)')
            plt.title('Memory Usage vs TPS Correlation')
            plt.grid(True, alpha=0.3)
            
            # Add correlation coefficient
            corr = merged['tps'].corr(merged['memory_mb'])
            plt.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=plt.gca().transAxes,
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
            
            plt.tight_layout()
            
            output_file = f"{output_dir}/system_vs_tps_{ts}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 System vs TPS chart saved: {output_file}")
        except Exception as e:
            print(f"⚠️  Error processing correlation for {ts}: {e}")

def generate_error_analysis(results_dir, output_dir):
    """Generate error categorization report"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    error_files = glob.glob(f"{results_dir}/errors_*.csv")
    
    if not error_files:
        print("⚠️  No error files found")
        return
    
    all_errors = []
    for error_file in error_files:
        try:
            df = pd.read_csv(error_file)
            all_errors.append(df)
        except Exception as e:
            print(f"⚠️  Warning: Could not load {error_file}: {e}")
            continue
    
    if not all_errors:
        return
    
    errors_df = pd.concat(all_errors, ignore_index=True)
    error_summary = errors_df.groupby('error').size().reset_index(name='count')
    error_summary = error_summary.sort_values('count', ascending=False)
    
    output_file = f"{output_dir}/error_analysis.csv"
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
    
    # Create output directory early
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"📂 Loading results from: {args.results_dir}")
    results, transaction_files, system_files = load_results(args.results_dir)
    
    if not results:
        print("❌ No results found")
        sys.exit(1)
    
    print(f"✅ Found {len(results)} test runs")
    print(f"✅ Found {len(transaction_files)} transaction logs")
    print(f"✅ Found {len(system_files)} system metrics logs")
    
    # Generate master summary
    print("\n📊 Generating master summary...")
    generate_master_summary(results, args.output_dir)
    
    # Generate charts
    print("\n📊 Generating charts...")
    plot_latency_distribution(transaction_files, args.output_dir)
    plot_tps_over_time(transaction_files, args.output_dir)
    plot_latency_vs_tps(transaction_files, args.output_dir)
    
    # Generate system resource charts
    if system_files:
        print("\n📊 Generating system resource charts...")
        plot_system_resources_over_time(system_files, args.output_dir)
        plot_system_vs_tps(transaction_files, system_files, args.output_dir)
    else:
        print("\n⚠️  No system metrics found (run tests with updated load_test.py)")
    
    # Error analysis
    print("\n📊 Generating error analysis...")
    generate_error_analysis(args.results_dir, args.output_dir)
    
    print("\n✅ Analysis complete!")
    print(f"📂 Results in: {args.output_dir}/")
    
    # List generated files
    print(f"\n📁 Generated files:")
    for file in os.listdir(args.output_dir):
        print(f"   - {args.output_dir}/{file}")

if __name__ == '__main__':
    main()