"""Runs the analytics API in dev mode with auto-reload. Usage: python scripts/run_api.py"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("soccera.api.main:app", host="127.0.0.1", port=8000, reload=True)
