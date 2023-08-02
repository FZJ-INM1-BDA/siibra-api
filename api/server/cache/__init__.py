from .redis import CacheGzipRedis, terminate as redis_terminate, on_startup as redis_on_startup

class DummyCache:
    """Dummystore to be used if no store is available."""
    def get_value(self, *args):
        return None
    def set_value(self, *args):
        return None

def get_instance():
    """Get the store singleton"""
    try:
        redis_cache = CacheGzipRedis()
        if redis_cache is None or not redis_cache.is_connected:
            raise Exception(f"Nonetype redis cache")
        return redis_cache
    except Exception as e:
        return DummyCache()

def on_startup():
    """On startup call"""
    redis_on_startup()

def terminate():
    """On terminate call"""
    redis_terminate()
