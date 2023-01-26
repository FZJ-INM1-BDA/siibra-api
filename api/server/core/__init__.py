from . import atlas, space, parcellation, region
from ..const import PrefixedRouter

prefixed_routers = (
    PrefixedRouter(prefix="/atlases", router=atlas.router),
    PrefixedRouter(prefix="/spaces", router=space.router),
    PrefixedRouter(prefix="/parcellations", router=parcellation.router),
    PrefixedRouter(prefix="/regions", router=region.router),
)
