#!/usr/bin/env python3
"""Convenience script to run the HTTP smoke check outside of pytest.

Usage:
  WB_APP_URL=http://localhost:8503/ ./scripts/run_http_smoke.py
"""
import os
import sys
import requests

base = os.getenv("WB_APP_URL", "http://localhost:8501/")
url = base.rstrip("/") + "/?wb_action=btn:+250"
print(f"Checking {url}")
try:
    r = requests.get(url, timeout=5)
except Exception as e:
    print("Request failed:", e)
    sys.exit(2)
if r.status_code != 200:
    print("Unexpected status:", r.status_code)
    sys.exit(3)
if "Script execution error" in r.text:
    print("Detected 'Script execution error' in page output")
    sys.exit(4)
print("Smoke check passed: page loaded without script error")
sys.exit(0)
