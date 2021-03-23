import redis
import os

_host = 'brainscapes-redis'
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
            # CacheRedis.__r = redis.Redis(host='localhost', port=6379, password='')
            CacheRedis.__instance = self

    def is_connected(self):
        try:
            self.__r.ping()
        except:
            return False
        return True

    def renew_connection(self):
        self.__r = redis.Redis(host=_host, port=_port, password=_password)
        # self.__r = redis.Redis(host='localhost', port=6379, password='')

    def get_value(self, key):
        if self.is_connected():
            return self.__r.get(key)
        else:
            self.renew_connection()
            if self.is_connected():
                return self.__r.get(key)
            else:
                return None


if __name__ == '__main__':
    cache_redis = CacheRedis.get_instance()
    print(cache_redis.get_value('Multilevel Human Atlas-minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-25-MNI 152 ICBM 2009c Nonlinear Asymmetric-Area TE 2.1 (STG) - left hemisphere'))

# r = redis.Redis(host='localhost', port=6379, password='')
#
# r.set(
#     '{}-{}-{}-{}'.format(str(current_atlas), str(current_parcellation.id), str(current_space), str(c)),
#     json.dumps({
#         'centroid_mm': list(r_props.attrs['centroid_mm']),
#         'volume_mm': r_props.attrs['volume_mm'],
#         'surface_mm': r_props.attrs['surface_mm'],
#         'is_cortical': r_props.attrs['is_cortical']
#     })
# )


