from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server.util import SapiCustomRoute
from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.common import router_decorator
from api.models.vocabularies.genes import GeneModel
# from api.common.data_handlers.vocabularies.gene import get_genes
from api.common.data_handlers.features.misc import get_genes

TAGS= ["vocabularies"]
"""HTTP vocabularies tags"""

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)
"""HTTP vocabularies router"""

@router.get("/genes", response_model=Page[GeneModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_genes)
def genes(find:str=None, func=None):
    """HTTP get (filtered) genes"""
    if func is None:
        raise HTTPException(500, "func: None passed")
    return paginate(func(find=find))
