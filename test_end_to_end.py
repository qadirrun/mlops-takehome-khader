#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for MLOps Pipeline
Tests all components: API, Training, Database, Monitoring
"""

import requests
import json
import time
import sys
from typing import Dict, List

# Configuration
API_BASE_URL = "http://localhost:8000"
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def test_health_check() -> bool:
    """Test 1: Health Check Endpoint"""
    print_test("Health Check Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "ok":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_model_info() -> bool:
    """Test 2: Model Info Endpoint"""
    print_test("Model Info Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Model: {data.get('model_name', 'N/A')}")
            print_success(f"Version: {data.get('version', 'N/A')}")
            print_success(f"Environment: {data.get('environment', 'N/A')}")
            return True
        else:
            print_error(f"Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Model info error: {e}")
        return False

def test_prediction() -> Dict:
    """Test 3: Prediction Endpoint"""
    print_test("Prediction Endpoint")
    try:
        # Test with valid Iris data (setosa)
        payload = {"features": [5.1, 3.5, 1.4, 0.2]}
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Prediction: {data.get('prediction')}")
            print_success(f"Probability: {data.get('probability', 0):.4f}")
            print_success(f"Latency: {data.get('latency_ms', 0):.2f}ms")
            print_success(f"Request ID: {data.get('request_id', 'N/A')}")
            return data
        else:
            print_error(f"Prediction failed: {response.status_code}")
            return {}
    except Exception as e:
        print_error(f"Prediction error: {e}")
        return {}

def test_multiple_predictions() -> bool:
    """Test 4: Multiple Predictions (Load Test)"""
    print_test("Multiple Predictions (10 requests)")
    success_count = 0
    latencies = []

    test_samples = [
        [5.1, 3.5, 1.4, 0.2],  # setosa
        [6.7, 3.0, 5.2, 2.3],  # virginica
        [5.9, 3.0, 4.2, 1.5],  # versicolor
    ]

    try:
        for i in range(10):
            payload = {"features": test_samples[i % 3]}
            response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=10)
            if response.status_code == 200:
                success_count += 1
                latencies.append(response.json().get('latency_ms', 0))
            time.sleep(0.1)  # Small delay between requests

        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        print_success(f"Successful predictions: {success_count}/10")
        print_success(f"Average latency: {avg_latency:.2f}ms")
        return success_count >= 8  # Allow 2 failures
    except Exception as e:
        print_error(f"Multiple predictions error: {e}")
        return False

def test_prediction_logs() -> bool:
    """Test 5: Prediction Logs Endpoint (PostgreSQL)"""
    print_test("Prediction Logs (PostgreSQL)")
    try:
        response = requests.get(f"{API_BASE_URL}/logs?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            logs = data.get('logs', [])
            print_success(f"Total logs in database: {count}")
            if logs:
                latest = logs[0]
                print_success(f"Latest log - Request ID: {latest.get('request_id', 'N/A')}")
                print_success(f"Latest log - Model: {latest.get('model_name', 'N/A')}")
                print_success(f"Latest log - Latency: {latest.get('latency_ms', 0)}ms")
            return count > 0
        else:
            print_error(f"Logs endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Logs endpoint error: {e}")
        return False

def test_prometheus_metrics() -> bool:
    """Test 6: Prometheus Metrics"""
    print_test("Prometheus Metrics Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/metrics-prometheus", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            # Check for key metrics
            required_metrics = [
                'iris_requests_total',
                'iris_predictions_total',
                'iris_request_latency_seconds',
                'iris_model_loaded'
            ]
            found_metrics = [m for m in required_metrics if m in metrics_text]
            print_success(f"Found {len(found_metrics)}/{len(required_metrics)} required metrics")
            for metric in found_metrics:
                print_success(f"  ✓ {metric}")
            return len(found_metrics) >= 3
        else:
            print_error(f"Metrics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Metrics endpoint error: {e}")
        return False


def test_prometheus_scraping() -> bool:
    """Test 7: Prometheus Scraping"""
    print_test("Prometheus Scraping")
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": "iris_requests_total"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                results = data.get('data', {}).get('result', [])
                print_success(f"Prometheus scraping working: {len(results)} metrics found")
                return True
        print_warning("Prometheus may not be scraping yet")
        return False
    except Exception as e:
        print_warning(f"Prometheus check skipped: {e}")
        return False

def test_grafana() -> bool:
    """Test 8: Grafana Availability"""
    print_test("Grafana Availability")
    try:
        response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print_success("Grafana is running")
            return True
        else:
            print_warning("Grafana may not be ready")
            return False
    except Exception as e:
        print_warning(f"Grafana check skipped: {e}")
        return False

def test_database_connection() -> bool:
    """Test 9: Database Connection"""
    print_test("Database Connection")
    try:
        response = requests.get(f"{API_BASE_URL}/logs?limit=1", timeout=10)
        if response.status_code == 200:
            print_success("PostgreSQL connection working")
            return True
        else:
            print_error(f"Database connection failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Database connection error: {e}")
        return False

def run_all_tests():
    """Run all end-to-end tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🚀 MLOps Pipeline - End-to-End Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

    tests = [
        ("Health Check", test_health_check),
        ("Model Info", test_model_info),
        ("Single Prediction", test_prediction),
        ("Multiple Predictions", test_multiple_predictions),
        ("Prediction Logs (PostgreSQL)", test_prediction_logs),
        ("Prometheus Metrics", test_prometheus_metrics),
        ("Prometheus Scraping", test_prometheus_scraping),
        ("Grafana Availability", test_grafana),
        ("Database Connection", test_database_connection),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
        time.sleep(0.5)

    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{status} - {name}")

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    percentage = (passed / total * 100) if total > 0 else 0

    if percentage >= 80:
        print(f"{Colors.GREEN}✅ Overall: {passed}/{total} tests passed ({percentage:.1f}%){Colors.RESET}")
        print(f"{Colors.GREEN}🎉 Pipeline is working end-to-end!{Colors.RESET}")
        return 0
    elif percentage >= 60:
        print(f"{Colors.YELLOW}⚠️  Overall: {passed}/{total} tests passed ({percentage:.1f}%){Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️  Some components need attention{Colors.RESET}")
        return 1
    else:
        print(f"{Colors.RED}❌ Overall: {passed}/{total} tests passed ({percentage:.1f}%){Colors.RESET}")
        print(f"{Colors.RED}❌ Pipeline has critical issues{Colors.RESET}")
        return 2

if __name__ == "__main__":
    sys.exit(run_all_tests())
