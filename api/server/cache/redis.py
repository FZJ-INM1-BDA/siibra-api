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
from threading import Timer
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
        return self._r.get(key)
        
    def set_value(self, key, value):
        if _is_ci or not self.is_connected:
            return None
        return self._r.set(key, value)


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

