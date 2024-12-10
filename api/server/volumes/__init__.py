from . import parcellationmap
from . import maps
from ..const import PrefixedRouter

prefixed_routers = (
    PrefixedRouter(prefix="/map", router=parcellationmap.router),
    PrefixedRouter(prefix="/maps", router=maps.router),
)
