import requests
import argparse
from datetime import datetime
import sys
from typing import List, Tuple

def check_url(url: str) -> Tuple[str, int, str, float]:
    """
    Check the health of a single URL.
    Returns a tuple containing:
    - URL
    - Status code
    - Response time (ms)
    - Error message (if any)
    """
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=10)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        return (url, response.status_code, f"{response_time:.2f}ms", "")
    except requests.exceptions.Timeout:
        return (url, -1, "", "Request timed out")
    except requests.exceptions.RequestException as e:
        return (url, -1, "", str(e))

def check_urls(urls: List[str]) -> List[Tuple[str, int, str, str]]:
    """Check multiple URLs and return their health status."""
    results = []
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        result = check_url(url)
        results.append(result)
    return results

def main():
    parser = argparse.ArgumentParser(description='URL Health Checker')
    parser.add_argument('urls', nargs='+', help='URLs to check')
    args = parser.parse_args()
    
    results = check_urls(args.urls)
    
    print("\nURL Health Check Results:")
    print("-" * 80)
    print(f"{'URL':<50} {'Status':<10} {'Response Time':<15} {'Error'}")
    print("-" * 80)
    
    for url, status, response_time, error in results:
        if status == 200:
            status_color = "\033[92m"  # Green
        elif status >= 400:
            status_color = "\033[91m"  # Red
        else:
            status_color = "\033[93m"  # Yellow
        
        status_display = f"{status_color}{status}\033[0m" if status >= 0 else "-"
        print(f"{url:<50} {status_display:<10} {response_time:<15} {error}")

if __name__ == "__main__":
    main()
