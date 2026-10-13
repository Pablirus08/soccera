"""Runs the live-polling loop forever. Usage: python scripts/run_live_poll.py"""

from soccera.ingestion.providers.api_football.adapter import ApiFootballAdapter
from soccera.ingestion.sync.live import run_live_poll_forever
from soccera.logging import configure_logging


def main() -> None:
    configure_logging()
    adapter = ApiFootballAdapter()
    try:
        run_live_poll_forever(adapter)
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
