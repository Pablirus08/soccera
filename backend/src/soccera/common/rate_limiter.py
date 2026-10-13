import threading
import time
from collections import deque


class RateLimiter:
    """
    Sliding-window rate limiter: blocks the caller until fewer than
    `max_calls` calls have happened in the trailing `period_seconds`.
    Thread-safe so it can guard a shared HTTP client.
    """

    def __init__(self, max_calls: int, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._call_times: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            while self._call_times and now - self._call_times[0] >= self.period_seconds:
                self._call_times.popleft()

            if len(self._call_times) >= self.max_calls:
                sleep_for = self.period_seconds - (now - self._call_times[0])
                if sleep_for > 0:
                    time.sleep(sleep_for)
                now = time.monotonic()
                while self._call_times and now - self._call_times[0] >= self.period_seconds:
                    self._call_times.popleft()

            self._call_times.append(time.monotonic())
