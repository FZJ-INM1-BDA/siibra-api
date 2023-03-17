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

from redis import Redis
import base64
from threading import Timer
import gzip
from typing import Union

from api.siibra_api_config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, IS_CI

_host = REDIS_HOST
_password = REDIS_PASSWORD
_port = REDIS_PORT
# do not use in ci
_is_ci = IS_CI

# Periodically updates the connected status
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CacheRedis:
    _r: Redis = None
    _is_connected = False
    _timer: RepeatTimer = None

    # read only property
    @property
    def is_connected(self):
        return self._is_connected

    def get_value(self, key):
        if _is_ci or not self.is_connected:
            return None
        bz64str = self._r.get(key)

        if bz64str is None:
            return None
        
        bz64str = CacheRedis.getstr(bz64str)
        # if cached value 
        if bz64str[0] == "{" and bz64str[-1] == "}":
            self.set_value(key, bz64str)
            return bz64str
        try:
            return CacheRedis.decode(bz64str)
        except:
            print(f"decoding key value error {key}, {bz64str}")
            return bz64str
    
    @staticmethod
    def getstr(val: Union[str, bytes]) -> str:
        if type(val) == str:
            return val
        if type(val) == bytes:
            return val.decode("utf-8")
        
        raise Exception(f"type {val.__class__.__name__} cannot be serialized")

    @staticmethod
    def getbytes(val: Union[str, bytes]) -> bytes:
        if type(val) == bytes:
            return val
        if type(val) == str:
            return bytes(val, "utf-8")
        
        raise Exception(f"type {val.__class__.__name__} cannot be serialized")

    @staticmethod
    def decode(val: Union[str, bytes]) -> str:
        bz64 = CacheRedis.getbytes(val)
        bz = base64.b64decode(bz64)
        b = gzip.decompress(bz)
        return b.decode("utf-8")

    @staticmethod
    def encode(val: Union[str, bytes]) -> str:
        b = CacheRedis.getbytes(val)
        bz = gzip.compress(b, compresslevel=9)
        bz64 = base64.b64encode(bz)
        bz64str = bz64.decode("utf-8")
        return bz64str
        
    def set_value(self, key, value):
        if _is_ci or not self.is_connected:
            return None
        
        compressed_value = CacheRedis.encode(value)
        return self._r.set(key, compressed_value)


def on_startup():
    CacheRedis._r = Redis(host=_host, port=_port, password=_password)
    def _heartbeat():
        try:
            CacheRedis._r.ping()
            CacheRedis._is_connected = True
        except Exception:
            CacheRedis._is_connected = False

    CacheRedis._timer = RepeatTimer(5, _heartbeat)
    CacheRedis._timer.start()

def terminate():
    if CacheRedis._timer is not None:
        CacheRedis._timer.cancel()

