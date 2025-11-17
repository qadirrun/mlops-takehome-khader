#!/usr/bin/env python3
"""
Health check script for Docker.

Checks if the API is responsive and the model is loaded.
"""

import sys
import requests

API_URL = "http://localhost:8000/healthz"


def main():
    """Perform the health check."""
    try:
        response = requests.get(API_URL, timeout=5)
        
        # Check for a successful status code
        if response.status_code != 200:
            print(f"Health check failed: Status code {response.status_code}")
            sys.exit(1)
        
        data = response.json()
        
        # Check if the model is loaded (key exists and is not None)
        if data.get("model") is None:
            print(f"Health check failed: Model not loaded yet. Response: {data}")
            sys.exit(1)
            
        print(f"Health check passed: {data}")
        sys.exit(0)

    except requests.exceptions.RequestException as e:
        print(f"Health check failed: Cannot connect to API. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

