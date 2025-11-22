#!/bin/bash

set -e

echo "========================================="
echo "🏥 Corda Health Records Benchmark Suite"
echo "========================================="
echo ""

# Get script directory (works from any location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python dependencies
echo "🔍 Checking dependencies..."
if ! python3 -c "import requests, faker, psutil, pandas, matplotlib" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Check if API is available
if ! curl -s -f http://localhost:50005/api/me > /dev/null 2>&1; then
    echo "❌ ERROR: API not available at http://localhost:50005/api"
    echo "Please start Corda nodes and web server:"
    echo "  Terminal 1: cd /workspaces/samples-java/health-records-cordapp/build/nodes && ./runnodes"
    echo "  Terminal 2: cd /workspaces/samples-java/health-records-cordapp && ./gradlew clients:runHospitalServer"
    exit 1
fi

echo "✅ API is available"
echo ""

# Create necessary directories
mkdir -p data results analysis

# Generate test data
echo "📊 Step 1: Generating test data (500 patients, 10 records each)..."
python3 generate_test_data.py --patients 1000 --records-per-patient 5 --output-dir data
echo ""

# Run baseline test (no rate limit)
echo "🚀 Step 2: Running baseline test (no rate limit)..."
python3 load_test.py \
    --patients data/patients.json \
    --records data/medical_records.json \
    --output-dir results/baseline \
    --max-retries 3
echo ""

# Run sustained load test
echo "🚀 Step 3: Running sustained load test (20 TPS)..."
python3 load_test.py \
    --patients data/patients.json \
    --records data/medical_records.json \
    --rate-limit 20 \
    --output-dir results/sustained \
    --max-retries 3
echo ""

# Run stress test
echo "🚀 Step 4: Running stress test (50 TPS)..."
python3 load_test.py \
    --patients data/patients.json \
    --records data/medical_records.json \
    --rate-limit 50 \
    --output-dir results/stress \
    --max-retries 3
echo ""

# Analyze all results
echo "📈 Step 5: Analyzing results..."
python3 analyze_results.py --results-dir results --output-dir analysis
echo ""

echo "========================================="
echo "✅ Benchmark Complete!"
echo "========================================="
echo ""
echo "📂 Results:"
echo "   Master Summary: analysis/master_summary.csv"
echo "   Charts: analysis/*.png"
echo "   Detailed Logs: results/*/"
echo ""
echo "📝 For your thesis:"
echo "   cat analysis/master_summary.csv"
echo "   ls analysis/*.png"
echo ""
echo "🔍 To investigate HTTP 500 errors:"
echo "   cat analysis/error_analysis.csv"
echo "   cat results/*/errors_*.csv"
echo ""