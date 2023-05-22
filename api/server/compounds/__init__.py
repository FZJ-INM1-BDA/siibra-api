from ..const import PrefixedRouter
from .download import router

prefixed_routers = (
    PrefixedRouter(prefix="/atlas_download", router=router),
)
