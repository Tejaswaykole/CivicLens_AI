"""Process-local limits for public authentication routes.

The counters live in this process. They reset when the process restarts and are
not shared across workers or hosts. A distributed deployment needs shared
storage behind the same `limits` window. Request bodies are not logged.
"""

from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter

_storage = MemoryStorage()
_windows = MovingWindowRateLimiter(_storage)


def reset_rate_limits() -> None:
    _storage.reset()


def allow(bucket: str, limit_text: str, identity: str) -> bool:
    item = parse(limit_text)
    return bool(_windows.hit(item, bucket, identity))
