"""Per-artefact build lock.

Prevents concurrent requests for the same artefact from each triggering the
ingestion service. Two backends, selected automatically the first time a lock
is taken by probing redis connectivity (see :func:`_resolve_backend`):

- **redis**: a distributed lock that works across processes/replicas. Required
  when the service is horizontally scaled (e.g. behind a HorizontalPodAutoscaler)
  — an in-process lock cannot coordinate across pods. Used when the ``hpa`` extra
  (redis) is installed and the configured redis host answers a ping.
- **threading**: an in-process lock, used as the fallback when redis is not
  reachable. Correct only for a single instance; concurrent replicas would not
  see each other's locks.

Both backends are exposed through the same :func:`build_lock` context manager,
which acquires non-blocking and yields whether the lock was acquired. A caller
that receives ``False`` should assume another worker already owns the build and
skip its own.
"""

from contextlib import contextmanager
import threading

from api.common.logger import logger
from api.siibra_api_config import SIIBRA_API_ARTEFACT_LOCK_TTL, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

_KEY_PREFIX = "geomsvc:artefact-lock:"

# How long the one-off connectivity probe (and the lock client's socket) may
# block before we give up and fall back to the threading backend.
_REDIS_CONNECT_TIMEOUT = 5

# Registry of per-key in-process locks for the threading backend.
_thread_locks: dict[str, threading.Lock] = {}
_registry_lock = threading.Lock()

# The lock backend is resolved once, lazily, by probing redis connectivity;
# ``None`` means "not yet resolved". ``_redis_client`` is set alongside it when
# the probe succeeds. Guarded by ``_backend_lock`` so the probe runs only once.
_backend = None
_redis_client = None
_backend_lock = threading.Lock()


def _get_thread_lock(key: str) -> threading.Lock:
    with _registry_lock:
        return _thread_locks.setdefault(key, threading.Lock())


def _resolve_backend():
    """Pick the lock backend once, preferring redis when it is reachable.

    Builds a redis client and pings it a single time. On success the distributed
    :func:`_redis_lock` is used; on any redis error (unreachable host, auth, the
    ``hpa`` extra not installed) we log and fall back to the in-process
    :func:`_threading_lock`. The result is memoized for the process lifetime, so
    the probe runs at most once.
    """
    global _backend, _redis_client
    if _backend is not None:
        return _backend
    with _backend_lock:
        if _backend is not None:
            return _backend

        try:
            import redis  # optional `hpa` extra; imported only when probing

            client = redis.Redis(
                host=REDIS_HOST,
                port=int(REDIS_PORT),
                password=REDIS_PASSWORD or None,
                socket_connect_timeout=_REDIS_CONNECT_TIMEOUT,
            )
            client.ping()
        except Exception as e:  # noqa: BLE401 - any failure means "use threading"
            logger.warning(
                "Redis lock backend unavailable (%s); falling back to the "
                "in-process threading lock. This is only safe for a single "
                "instance — concurrent replicas will not coordinate.",
                e,
            )
            _backend = _threading_lock
        else:
            _redis_client = client
            _backend = _redis_lock
        return _backend


@contextmanager
def _redis_lock(key: str):
    import redis  # for redis.exceptions

    lock = _redis_client.lock(
        f"{_KEY_PREFIX}{key}",
        timeout=SIIBRA_API_ARTEFACT_LOCK_TTL,
        blocking=False,
    )
    acquired = lock.acquire()
    try:
        yield acquired
    finally:
        if acquired:
            try:
                lock.release()
            except redis.exceptions.LockError:
                # TTL elapsed mid-build; expiry already released it.
                ...


@contextmanager
def _threading_lock(key: str):
    lock = _get_thread_lock(key)
    acquired = lock.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()


@contextmanager
def lock_key(key: str):
    """Acquire a non-blocking per-``key`` lock; yield whether it was acquired.

    Usage::

        with build_lock(artefact_key) as acquired:
            if not acquired:
                return  # another worker owns this build
            ...
    """
    backend = _resolve_backend()
    with backend(key) as acquired:
        yield acquired
