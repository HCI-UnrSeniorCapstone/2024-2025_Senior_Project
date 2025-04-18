import requests
import sys
import time
import socket
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables for configuration
load_dotenv()


# Set up logging
def log(message):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


# Check multiple backend URLs
backend_urls = [
    "http://100.82.85.28:5004",  # Original config IP
    "http://172.20.199.82:5004",  # Server IP from logs
    "http://localhost:5004",  # Localhost
    "http://127.0.0.1:5004",  # Localhost via IPv4
]


def check_port(host, port, timeout=2):
    """Test if a port is open on a host"""
    log(f"Testing TCP connection to {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    start_time = time.time()
    result = sock.connect_ex((host, port))
    end_time = time.time()

    elapsed = (end_time - start_time) * 1000  # in milliseconds

    sock.close()

    if result == 0:
        log(f"✅ Port {port} on {host} is OPEN (responded in {elapsed:.2f}ms)")
        return True
    else:
        log(
            f"❌ Port {port} on {host} is CLOSED or filtered (check took {elapsed:.2f}ms)"
        )
        return False


def test_endpoint(url, timeout=5):
    """Test if an endpoint is reachable"""
    log(f"Testing HTTP connection to {url}...")
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        end = time.time()
        elapsed = (end - start) * 1000  # in milliseconds

        log(f"✅ Connected in {elapsed:.2f}ms, Status: {response.status_code}")
        if response.status_code == 200:
            try:
                log(f"Response: {response.json()}")
            except:
                log(f"Response not JSON: {response.text[:100]}")
        return True
    except requests.exceptions.Timeout:
        log(f"❌ Connection timed out after {timeout}s")
    except requests.exceptions.ConnectionError:
        log(f"❌ Connection refused")
    except Exception as e:
        log(f"❌ Error: {e}")
    return False


def run_all_tests():
    """Run all connectivity tests"""
    log("====== Testing TCP Ports ======")
    # Test ports on different hosts
    check_port("100.82.85.28", 5004)  # Original config IP
    check_port("172.20.199.82", 5004)  # Server IP from logs
    check_port("localhost", 5004)  # Localhost
    check_port("127.0.0.1", 5004)  # Localhost via IPv4

    # Test database ports
    db_host = os.getenv("MYSQL_HOST", "localhost")
    check_port(db_host, 3306)  # MySQL port

    log("\n====== Testing HTTP Endpoints ======")
    # Test endpoint on different URLs
    endpoints = [
        "/api/ping",
        "/api/analytics/ping",
        "/api/analytics/health",
        "/api/analytics/studies",
    ]

    results = {}

    for base_url in backend_urls:
        log(f"\nTesting endpoints on {base_url}")
        success_count = 0

        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            if test_endpoint(url):
                success_count += 1

        results[base_url] = {
            "success": success_count,
            "total": len(endpoints),
            "success_rate": f"{(success_count / len(endpoints)) * 100:.1f}%",
        }

    # Print summary
    log("\n====== Summary ======")
    for url, result in results.items():
        log(
            f"{url}: {result['success']}/{result['total']} endpoints reachable ({result['success_rate']})"
        )

    # Find best URL
    best_url = max(results.items(), key=lambda x: x[1]["success"])
    log(f"\nBest performing URL: {best_url[0]} ({best_url[1]['success_rate']})")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--tcp":
            # Just test TCP ports
            for host in ["100.82.85.28", "172.20.199.82", "localhost", "127.0.0.1"]:
                check_port(host, 5004)
        elif sys.argv[1] == "--http":
            # Just test HTTP
            for base_url in backend_urls:
                test_endpoint(f"{base_url}/api/analytics/ping")
        elif sys.argv[1].startswith("http"):
            # Test specific URL
            test_endpoint(sys.argv[1])
        else:
            # Test specific host:port
            parts = sys.argv[1].split(":")
            if len(parts) == 2:
                check_port(parts[0], int(parts[1]))
            else:
                log(f"Invalid format. Use host:port, --tcp, --http, or a URL")
    else:
        # Run all tests
        results = run_all_tests()

        # Find if any URL was successful
        any_success = any(r["success"] > 0 for r in results.values())
        sys.exit(0 if any_success else 1)
