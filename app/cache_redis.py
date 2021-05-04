import redis
import os

_host = 'siibra-redis'
_password = os.getenv('REDIS_PASSWORD')
_port = 6379


class CacheRedis:
    __instance = None
    __r = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if CacheRedis.__instance is None:
            CacheRedis()
        return CacheRedis.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if CacheRedis.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CacheRedis.__r = redis.Redis(host=_host, port=_port, password=_password)
            CacheRedis.__instance = self

    def is_connected(self):
        try:
            self.__r.ping()
        except:
            return False
        return True

    def renew_connection(self):
        self.__r = redis.Redis(host=_host, port=_port, password=_password)

    def get_value(self, key):
        if self.is_connected():
            return self.__r.get(key)
        else:
            self.renew_connection()
            if self.is_connected():
                return self.__r.get(key)
            else:
                return None
