from . import parcellationmap
from ..const import PrefixedRouter

prefixed_routers = (
    PrefixedRouter(prefix="/map", router=parcellationmap.router),
)
