#!/usr/bin/env python3
"""
Library Book Usage Analysis System
Main launcher script.
Starts FastAPI backend server with Uvicorn and automatically serves the React UI.
"""
import sys
import webbrowser
from threading import Timer
import uvicorn
from backend.config import config

def open_browser():
    url = f"http://{config.APP_HOST}:{config.APP_PORT}"
    print(f"\n=======================================================")
    print(f"  Library Book Usage Analysis System is LIVE!")
    print(f"  Web Dashboard:       {url}")
    print(f"  Interactive API Docs: {url}/docs")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    # Schedule browser open after 1.5 seconds
    Timer(1.5, open_browser).start()
    uvicorn.run(
        "backend.main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG
    )
