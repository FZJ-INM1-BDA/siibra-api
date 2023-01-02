from .redis import CacheRedis, terminate as redis_terminate, on_startup as redis_on_startup

class DummyCache:
    def get_value(self, *args):
        return None
    def set_value(self, *args):
        return None

def get_instance():
    try:
        redis_cache = CacheRedis()
        if redis_cache is None or not redis_cache.is_connected:
            raise Exception(f"Nonetype redis cache")
        return redis_cache
    except Exception as e:
        return DummyCache()

def on_startup():
    redis_on_startup()

def terminate():
    redis_terminate()
