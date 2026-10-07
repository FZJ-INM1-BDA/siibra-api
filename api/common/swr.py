import time
import threading
from typing import Callable, Dict, Generic, Hashable, Set, Tuple, TypeVar

from api.common import general_logger

T = TypeVar("T")


class StaleWhileRevalidate(Generic[T]):
    """In-process, thread-safe stale-while-revalidate cache.

    On :meth:`get`:

    - if nothing is cached for the key, ``fetch`` is called synchronously and
      the result stored (the caller waits for the cold fetch);
    - if the cached value is younger than ``ttl``, it is returned as-is;
    - if it is older than ``ttl``, the (stale) cached value is returned
      immediately and a single background refresh is kicked off. Concurrent
      requests for the same key coalesce onto that one refresh, so a key is
      refreshed at most once per ``ttl`` window.

    The cache is per-process: each worker maintains its own copy.
    """

    def __init__(self, ttl: float = 5.0) -> None:
        self._ttl = ttl
        self._lock = threading.Lock()
        self._store: Dict[Hashable, Tuple[float, T]] = {}
        self._refreshing: Set[Hashable] = set()

    def get(self, key: Hashable, fetch: Callable[[], T]) -> T:
        with self._lock:
            entry = self._store.get(key)

        if entry is None:
            value = fetch()
            with self._lock:
                self._store[key] = (time.monotonic(), value)
            return value

        ts, value = entry
        if (time.monotonic() - ts) >= self._ttl:
            self._schedule_refresh(key, fetch)
        return value

    def _schedule_refresh(self, key: Hashable, fetch: Callable[[], T]) -> None:
        with self._lock:
            if key in self._refreshing:
                return
            self._refreshing.add(key)

        def _run() -> None:
            try:
                value = fetch()
                with self._lock:
                    self._store[key] = (time.monotonic(), value)
            except Exception:
                # keep serving the stale value; just log and retry next window
                general_logger.exception("swr background refresh failed for %s", key)
            finally:
                with self._lock:
                    self._refreshing.discard(key)

        threading.Thread(target=_run, daemon=True, name="swr-refresh").start()
