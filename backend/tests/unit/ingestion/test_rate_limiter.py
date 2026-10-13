import time

from soccera.common.rate_limiter import RateLimiter


def test_allows_calls_up_to_limit_without_blocking():
    limiter = RateLimiter(max_calls=3, period_seconds=1.0)
    start = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    assert time.monotonic() - start < 0.5


def test_blocks_once_limit_exceeded_within_window():
    limiter = RateLimiter(max_calls=2, period_seconds=0.3)
    limiter.acquire()
    limiter.acquire()

    start = time.monotonic()
    limiter.acquire()
    elapsed = time.monotonic() - start

    assert elapsed >= 0.2
