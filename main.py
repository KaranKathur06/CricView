"""
CricView — Deployment Entrypoint
==================================
This file allows deployment platforms (Railway, Render, Heroku, etc.)
to start the Streamlit app via `python main.py`.
"""

import os
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "8501")

    os.execvp(
        sys.executable,
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            f"--server.port={port}",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
    )
