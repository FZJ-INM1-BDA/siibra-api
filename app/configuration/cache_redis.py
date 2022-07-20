# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import redis
import os

_host = os.getenv("SIIBRA_REDIS_SERVICE_HOST") or os.getenv("REDIS_SERVICE_HOST") or "siibra-redis"
_password = os.getenv("REDIS_PASSWORD")
_port = os.getenv("SIIBRA_REDIS_SERVICE_PORT") or os.getenv("REDIS_SERVICE_PORT") or 6379
# do not use in ci
_is_ci = os.getenv("CI") is not None


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
            CacheRedis.__r = redis.Redis(
                host=_host, port=_port, password=_password)
            CacheRedis.__instance = self

    @property
    def is_connected(self):
        try:
            self.__r.ping()
        except BaseException:
            return False
        return True

    def renew_connection(self):
        self.__r = redis.Redis(host=_host, port=_port, password=_password)

    def get_value(self, key):
        if _is_ci:
            return None
        if not self.is_connected:
            self.renew_connection()
        return self.__r.get(key)
        
    def set_value(self, key, value):
        if _is_ci:
            return None
        if not self.is_connected:
            self.renew_connection()
        return self.__r.set(key, value)
