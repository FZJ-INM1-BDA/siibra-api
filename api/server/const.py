from collections import namedtuple
from api.siibra_api_config import __version__

FASTAPI_VERSION = (3, 0)
"""siibra-api version"""

PrefixedRouter = namedtuple("PrefixedRouter", ["prefix", "router"])

cache_header = "x-fastapi-cache"
