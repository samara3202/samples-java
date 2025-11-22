#!/usr/bin/env python3
"""
Load testing engine for Corda Health Records
Measures TPS, latency, CPU, memory, and generates metrics
Enhanced with retry logic and detailed error handling
"""

import requests
import json
import time
import csv
import statistics
import threading
import psutil
import os
import sys
from datetime import datetime
from collections import defaultdict
import argparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PerformanceMetrics:
    def __init__(self):
        self.transactions = []
        self.errors = []
        self.cpu_samples = []
        self.memory_samples = []
        self.system_samples = []
        self.start_time = None
        self.end_time = None
        self.lock = threading.Lock()

    def add_transaction(self, tx_type, latency, success, error_msg=None, status_code=None, response_body=None):
        with self.lock:
            timestamp = time.time()
            self.transactions.append({
                'timestamp': timestamp,
                'type': tx_type,
                'latency': latency,
                'success': success,
                'error': error_msg,
                'status_code': status_code,
                'response_body': response_body
            })
            
            if not success:
                self.errors.append({
                    'timestamp': timestamp,
                    'type': tx_type,
                    'error': error_msg,
                    'status_code': status_code,
                    'response_body': response_body
                })

    def add_system_sample(self, cpu, memory):
        with self.lock:
            timestamp = time.time()
            self.cpu_samples.append(cpu)
            self.memory_samples.append(memory)
            self.system_samples.append({
                'timestamp': timestamp,
                'cpu_percent': cpu,
                'memory_mb': memory / (1024 * 1024)
            })

class LoadTester:
    def __init__(self, base_url, metrics, max_retries=3, backoff_factor=0.5):
        self.base_url = base_url
        self.metrics = metrics
        
        # Configure retry strategy
        retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST"]  # ✅ USE THIS INSTEAD
        )
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=100, pool_connections=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def create_patient(self, patient_data):
        """Create a patient record with retry logic"""
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/patients",
                json=patient_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            latency = time.time() - start
            
            success = response.status_code in [200, 201]
            error_msg = None if success else f"HTTP {response.status_code}"
            status_code = response.status_code
            response_body = response.text[:200] if not success else None
            
            self.metrics.add_transaction('create_patient', latency, success, error_msg, status_code, response_body)
            return success, response.text if success else error_msg
            
        except requests.exceptions.RequestException as e:
            latency = time.time() - start
            self.metrics.add_transaction('create_patient', latency, False, f"Request failed: {str(e)}", None, None)
            return False, str(e)
        except Exception as e:
            latency = time.time() - start
            self.metrics.add_transaction('create_patient', latency, False, f"Unexpected error: {str(e)}", None, None)
            return False, str(e)

    def create_medical_record(self, patient_id, record_data):
        """Create a medical record with retry logic"""
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/patients/{patient_id}/records",
                json=record_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            latency = time.time() - start
            
            success = response.status_code in [200, 201]
            error_msg = None if success else f"HTTP {response.status_code}"
            status_code = response.status_code
            response_body = response.text[:200] if not success else None
            
            self.metrics.add_transaction('create_record', latency, success, error_msg, status_code, response_body)
            return success, response.text if success else error_msg
            
        except requests.exceptions.RequestException as e:
            latency = time.time() - start
            self.metrics.add_transaction('create_record', latency, False, f"Request failed: {str(e)}", None, None)
            return False, str(e)
        except Exception as e:
            latency = time.time() - start
            self.metrics.add_transaction('create_record', latency, False, f"Unexpected error: {str(e)}", None, None)
            return False, str(e)

    def get_patient_records(self, patient_id):
        """Retrieve patient records (sampled) with retry logic"""
        start = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/patients/{patient_id}/records",
                timeout=10,
                headers={'Accept': 'application/json'}
            )
            latency = time.time() - start
            
            success = response.status_code == 200
            error_msg = None if success else f"HTTP {response.status_code}"
            status_code = response.status_code
            response_body = response.text[:200] if not success else None
            
            self.metrics.add_transaction('get_records', latency, success, error_msg, status_code, response_body)
            return success, response.text if success else error_msg
            
        except requests.exceptions.RequestException as e:
            latency = time.time() - start
            self.metrics.add_transaction('get_records', latency, False, f"Request failed: {str(e)}", None, None)
            return False, str(e)
        except Exception as e:
            latency = time.time() - start
            self.metrics.add_transaction('get_records', latency, False, f"Unexpected error: {str(e)}", None, None)
            return False, str(e)

    def monitor_system(self):
        """Monitor CPU and memory usage"""
        process = psutil.Process(os.getpid())
        
        while True:
            if hasattr(self.metrics, 'stop_monitoring') and self.metrics.stop_monitoring:
                break
                
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = process.memory_info().rss
                self.metrics.add_system_sample(cpu, memory)
                time.sleep(1)
            except Exception as e:
                print(f"Warning: System monitoring error: {e}")
                time.sleep(1)

def calculate_tps_windows(transactions, start_time, end_time):
    """Calculate TPS in 1-second windows"""
    successful = [tx for tx in transactions if tx['success']]
    
    if not successful:
        return []
    
    # Create 1-second windows
    tps_windows = []
    window_start = start_time
    
    while window_start < end_time:
        window_end = window_start + 1.0
        window_txs = [tx for tx in successful 
                     if window_start <= tx['timestamp'] < window_end]
        tps_windows.append(len(window_txs))
        window_start = window_end
    
    return tps_windows

def run_load_test(base_url, patients_file, records_file, rate_limit=None, sample_interval=10, max_retries=3):
    """Execute the load test"""
    
    print("\n" + "="*60)
    print("🏥 Corda Health Records Load Test")
    print("="*60)
    print(f"API: {base_url}")
    print(f"Patients: {patients_file}")
    print(f"Records: {records_file}")
    print(f"Rate Limit: {rate_limit or 'None'} TPS")
    print(f"Sample Interval: Every {sample_interval}th transaction")
    print(f"Max Retries: {max_retries}")
    print("="*60)
    
    # Load test data
    try:
        with open(patients_file, 'r') as f:
            patients = json.load(f)
        
        with open(records_file, 'r') as f:
            records = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Error: Test data file not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in test data: {e}")
        sys.exit(1)
    
    # Group records by patient
    records_by_patient = defaultdict(list)
    for record in records:
        records_by_patient[record['patientId']].append(record)
    
    # Initialize metrics and tester
    metrics = PerformanceMetrics()
    tester = LoadTester(base_url, metrics, max_retries=max_retries)
    
    # Start system monitoring
    monitor_thread = threading.Thread(target=tester.monitor_system, daemon=True)
    monitor_thread.start()
    
    # Start test
    metrics.start_time = time.time()
    print(f"\n🚀 Starting load test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tx_count = 0
    success_count = 0
    
    for i, patient in enumerate(patients):
        # Create patient
        success, message = tester.create_patient(patient)
        tx_count += 1
        
        if success:
            success_count += 1
            # Create medical records for this patient
            patient_records = records_by_patient.get(patient['patientId'], [])
            
            for j, record in enumerate(patient_records):
                # Sample every Nth transaction for retrieval
                if (tx_count % sample_interval) == 0:
                    tester.get_patient_records(patient['patientId'])
                
                record_success, record_message = tester.create_medical_record(patient['patientId'], record)
                tx_count += 1
                
                if record_success:
                    success_count += 1
                
                # Rate limiting
                if rate_limit:
                    time.sleep(1.0 / rate_limit)
        else:
            print(f"⚠️  Failed to create patient {patient['patientId']}: {message}")
        
        # Progress display
        if (i + 1) % 100 == 0:
            elapsed = time.time() - metrics.start_time
            current_tps = tx_count / elapsed if elapsed > 0 else 0
            error_rate = (tx_count - success_count) / tx_count * 100 if tx_count > 0 else 0
            print(f"📊 Progress: {i+1}/{len(patients)} patients | {tx_count} tx | TPS: {current_tps:.2f} | Errors: {error_rate:.1f}%")
    
    metrics.end_time = time.time()
    metrics.stop_monitoring = True
    
    # Wait for monitor thread to finish
    monitor_thread.join(timeout=5)
    
    print(f"\n✅ Load test complete!")
    print(f"Total transactions: {tx_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {tx_count - success_count}")
    print(f"Duration: {metrics.end_time - metrics.start_time:.2f} seconds")
    
    return metrics

def save_results(metrics, output_dir):
    """Save test results to files"""
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate final metrics
    results = calculate_metrics(metrics)
    
    # Save summary JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"{output_dir}/summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Summary saved: {summary_file}")
    
    # Save transactions CSV
    tx_file = f"{output_dir}/transactions_{timestamp}.csv"
    with open(tx_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'latency', 'success', 'error', 'status_code', 'response_body'])
        writer.writeheader()
        writer.writerows(metrics.transactions)
    print(f"💾 Transactions saved: {tx_file}")
    
    # Save system metrics CSV (NEW)
    if metrics.system_samples:
        system_file = f"{output_dir}/system_{timestamp}.csv"
        with open(system_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'cpu_percent', 'memory_mb'])
            writer.writeheader()
            writer.writerows(metrics.system_samples)
        print(f"💾 System metrics saved: {system_file}")
    
    # Save errors CSV (if any)
    if metrics.errors:
        error_file = f"{output_dir}/errors_{timestamp}.csv"
        with open(error_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'error', 'status_code', 'response_body'])
            writer.writeheader()
            writer.writerows(metrics.errors)
        print(f"💾 Errors saved: {error_file}")
    
    return results

def calculate_metrics(metrics):
    """Calculate all performance metrics"""
    if not metrics.transactions:
        return {'error': 'No transactions recorded'}
    
    successful = [tx for tx in metrics.transactions if tx['success']]
    latencies = [tx['latency'] for tx in successful]
    
    if not latencies:
        return {'error': 'No successful transactions'}
    
    # Time metrics
    duration = metrics.end_time - metrics.start_time
    
    # TPS calculations
    total_txs = len(successful)
    mean_tps = total_txs / duration if duration > 0 else 0
    tps_windows = calculate_tps_windows(metrics.transactions, metrics.start_time, metrics.end_time)
    median_tps = statistics.median(tps_windows) if tps_windows else 0
    
    # Latency calculations (convert to milliseconds)
    avg_latency_ms = statistics.mean(latencies) * 1000
    median_latency_ms = statistics.median(latencies) * 1000
    p95_latency_ms = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies) * 1000
    std_dev_latency_ms = statistics.stdev(latencies) * 1000 if len(latencies) > 1 else 0
    
    # System metrics
    avg_cpu = statistics.mean(metrics.cpu_samples) if metrics.cpu_samples else 0
    peak_memory_mb = max(metrics.memory_samples) / (1024 * 1024) if metrics.memory_samples else 0
    
    # Error analysis
    error_rate = len(metrics.errors) / len(metrics.transactions) * 100
    error_types = defaultdict(int)
    for error in metrics.errors:
        error_key = f"HTTP {error.get('status_code', 'Unknown')}" if error.get('status_code') else error.get('error', 'Unknown')
        error_types[error_key] += 1
    
    return {
        'duration_seconds': duration,
        'total_transactions': total_txs,
        'failed_transactions': len(metrics.errors),
        'mean_tps': mean_tps,
        'median_tps': median_tps,
        'avg_latency_ms': avg_latency_ms,
        'median_latency_ms': median_latency_ms,
        'p95_latency_ms': p95_latency_ms,
        'std_dev_latency_ms': std_dev_latency_ms,
        'avg_cpu_percent': avg_cpu,
        'peak_memory_mb': peak_memory_mb,
        'error_rate_percent': error_rate,
        'error_types': dict(error_types)
    }

def display_results(results):
    """Display formatted results"""
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
        return
    
    print("\n" + "="*80)
    print("📈 PERFORMANCE METRICS SUMMARY")
    print("="*80)
    print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"📊 Total Transactions: {results['total_transactions']:,}")
    print(f"❌ Failed Transactions: {results['failed_transactions']:,}")
    
    print(f"\n🚀 Throughput:")
    print(f"   Mean TPS: {results['mean_tps']:.2f}")
    print(f"   Median TPS: {results['median_tps']:.2f}")
    
    print(f"\n⏱️  Latency:")
    print(f"   Average: {results['avg_latency_ms']:.2f} ms")
    print(f"   Median: {results['median_latency_ms']:.2f} ms")
    print(f"   P95: {results['p95_latency_ms']:.2f} ms")
    print(f"   Std Dev: {results['std_dev_latency_ms']:.2f} ms")
    
    print(f"\n💻 System Resources:")
    print(f"   Avg CPU: {results['avg_cpu_percent']:.2f}%")
    print(f"   Peak Memory: {results['peak_memory_mb']:.2f} MB")
    
    print(f"\n⚠️  Errors:")
    print(f"   Error Rate: {results['error_rate_percent']:.2f}%")
    if results['error_types']:
        print(f"   Error Types:")
        for error_type, count in results['error_types'].items():
            print(f"     {error_type}: {count}")
    
    print("="*80)

def main():
    parser = argparse.ArgumentParser(description='Load test Corda Health Records')
    parser.add_argument('--url', default='http://localhost:50005/api', help='API base URL')
    parser.add_argument('--patients', default='data/patients.json', help='Patients file')
    parser.add_argument('--records', default='data/medical_records.json', help='Records file')
    parser.add_argument('--rate-limit', type=float, help='Rate limit in TPS')
    parser.add_argument('--sample-interval', type=int, default=10, help='Sample every Nth transaction')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--max-retries', type=int, default=3, help='Max retries for failed requests')
    
    args = parser.parse_args()
    
    # Check if API is available
    try:
        response = requests.get(f"{args.url}/me", timeout=5)
        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API at {args.url}")
        print(f"Error: {e}")
        print("\nMake sure Corda nodes and web server are running:")
        print("  Terminal 1: cd build/nodes && ./runnodes")
        print("  Terminal 2: ./gradlew clients:runHospitalServer")
        sys.exit(1)
    
    print(f"✅ API available at {args.url}")
    
    # Run load test
    metrics = run_load_test(
        args.url,
        args.patients,
        args.records,
        args.rate_limit,
        args.sample_interval,
        args.max_retries
    )
    
    # Save and display results
    results = save_results(metrics, args.output_dir)
    display_results(results)

if __name__ == '__main__':
    main()