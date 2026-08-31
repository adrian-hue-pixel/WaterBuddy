import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def _wait_for_http(url: str, timeout: float = 25.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            return requests.get(url, timeout=2)
        except requests.RequestException:
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for app to respond at {url}")


def test_wb_smoke_http():
    """Simple HTTP smoke test that ensures the app responds to wb_action
    query-params without producing a Streamlit 'Script execution error' page.

    The app URL can be overridden with WB_APP_URL environment variable
    (default: http://localhost:8501/). If the app is not already running,
    this test launches it locally for the duration of the check.
    """
    base = os.getenv("WB_APP_URL", "http://localhost:8501/")
    url = base.rstrip("/") + "/?wb_action=btn:+250"

    proc = None
    try:
        response = _wait_for_http(url)
    except RuntimeError:
        project_root = Path(__file__).resolve().parents[2]
        proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8501"],
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        try:
            response = _wait_for_http(url)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=10)

    assert response.status_code == 200, f"Unexpected status {response.status_code} for {url}"
    text = response.text
    assert "Script execution error" not in text, "Page returned a Streamlit script execution error"
    # Basic sanity: the Streamlit shell root should be present (app is served)
    assert "<div id=\"root\">" in text or "<noscript>You need to enable JavaScript to run this app.</noscript>" in text
