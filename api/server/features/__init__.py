
from fastapi_pagination import paginate, Page
from fastapi_versioning import version
from fastapi.exceptions import HTTPException
from fastapi import Request, APIRouter
from pydantic import BaseModel
from typing import Union, Optional, List
from functools import partial
from enum import Enum
import re

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.common import router_decorator, async_router_decorator
from api.common.data_handlers.features.types import (
    all_feature_types, all_features, single_feature, get_single_feature_from_id, get_single_feature_plot_from_id
)
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel
from api.models.features._basetypes.cortical_profiles import SiibraCorticalProfileModel
from api.models.features.molecular.receptor_density_fingerprint import (
    SiibraReceptorDensityFp
)
from api.models.features._basetypes.tabular import (
    SiibraTabularModel
)
from api.models.features._basetypes.volume_of_interest import (
    SiibraVoiModel
)
from api.models.features.dataset.ebrains import (
    SiibraEbrainsDataFeatureModel
)
from api.common.exceptions import NotFound
from api.server.util import SapiCustomRoute
from .util import wrap_feature_category
from typing import List, Dict


TAGS= ["feature"]
"""HTTP feature tags"""

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)
"""HTTP feature router"""

class FeatureMetaModel(BaseModel):
    """Meta feature type"""
    name: str
    display_name: str
    path: Optional[str]
    query_params: Optional[List[str]]
    required_query_params: Optional[List[str]]
    optional_query_params: Optional[List[str]]
    path_params: Optional[List[str]]
    category: Optional[str]

class CategoryModel(BaseModel):
    """Category model"""
    name: str
    feature: List[FeatureMetaModel]

def depascal(input: str) -> str:
    """Pascal to snake
    
    Args:
        input: string in PascalCase
    
    Returns:
        string in snake_case"""
    if not input:
        return None
    return re.sub(
        r'([A-Z][A-Z]+)',
        r' \1',
        re.sub(
            r'([A-Z][a-z]+)',
            r' \1',
            input
        )
    ).strip()

def retrieve_routes(request: Request, feature_name: str) -> Dict:
    """Retrieve the meta info on feature types, given feature_name
    
    Args:
        feature_name: feature identifier (e.g. name)
    
    Returns:
        Meta info"""
    for f_name in feature_name.split(".")[::-1]:
        for route in request.app.routes:
            if route.path.endswith(f"/{f_name}"):
                return {
                    'path': route.path,
                    'query_params': [param.name for param in route.dependant.query_params],
                    'path_params': [param.name for param in route.dependant.path_params],
                    'required_query_params': [
                        param.name
                        for param in route.dependant.query_params
                        if param.required
                    ],
                    'optional_query_params': [
                        param.name
                        for param in route.dependant.query_params
                        if not param.required
                    ],
                }
    return {}

@router.get("/_types", response_model=Page[FeatureMetaModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_feature_types)
def get_all_feature_types(request: Request, func):
    """Get meta info of all feature types"""
    all_types = func()
    all_types = sorted(all_types, key=lambda obj: obj['name'])
    all_types = [{
        **retrieve_routes(request, item['name']),
        **item,
        'display_name': depascal(item['name'].split(".")[-1]),
    } for item in all_types]
    return paginate(all_types)


# Regional Connectivity
RegionalConnectivityModels = SiibraRegionalConnectivityModel

@router.get("/RegionalConnectivity", response_model=Page[RegionalConnectivityModels])
@version(*FASTAPI_VERSION)
@wrap_feature_category("RegionalConnectivity")
@async_router_decorator(ROLE, func=partial(all_features, space_id=None, region_id=None))
async def get_all_connectivity_features(parcellation_id: str, type: Optional[str]=None, func=lambda:[]):
    """Get all connectivity features"""
    type = str(type) if type else None
    return paginate(
        await func(parcellation_id=parcellation_id, type=type)
    )

@router.get("/RegionalConnectivity/{feature_id:lazy_path}", response_model=RegionalConnectivityModels, description="""
subject is an optional param.
If provided, the specific matrix will be return.
If not provided, the matrix averaged between subjects will be returned under the key _average.
""")
@version(*FASTAPI_VERSION)
@wrap_feature_category("RegionalConnectivity")
@async_router_decorator(ROLE, func=partial(single_feature, space_id=None, region_id=None))
async def get_single_connectivity_feature(parcellation_id: str, feature_id: str, subject: Optional[str]=None, type: Optional[str]=None, func=lambda:None):
    """Get single connectivity feature"""
    type = str(type) if type else None
    return await func(parcellation_id=parcellation_id, feature_id=feature_id, subject=subject, type=type)


# Cortical Profiles
CortialProfileModels = SiibraCorticalProfileModel

@router.get("/CorticalProfile", response_model=Page[CortialProfileModels])
@version(*FASTAPI_VERSION)
@wrap_feature_category("CorticalProfile")
@async_router_decorator(ROLE, func=partial(all_features, space_id=None))
async def get_all_corticalprofile_features(parcellation_id: str, region_id: str, type: Optional[str]=None, func=lambda:[]):
    """Get all CorticalProfile features"""
    type = str(type) if type else None
    return paginate(
        await func(parcellation_id=parcellation_id, region_id=region_id, type=type)
    )

@router.get("/CorticalProfile/{feature_id:lazy_path}", response_model=CortialProfileModels)
@version(*FASTAPI_VERSION)
@wrap_feature_category("CorticalProfile")
@async_router_decorator(ROLE, func=partial(single_feature, space_id=None))
async def get_single_corticalprofile_feature(parcellation_id: str, region_id: str, feature_id: str, type: Optional[str]=None, func=lambda:None):
    """Get a single CorticalProfile feature"""
    type = str(type) if type else None
    return await func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, type=type)



# Tabular
TabularModels = Union[SiibraCorticalProfileModel, SiibraReceptorDensityFp, SiibraTabularModel]

@router.get("/Tabular", response_model=Page[TabularModels])
@version(*FASTAPI_VERSION)
@wrap_feature_category("Tabular")
@async_router_decorator(ROLE, func=partial(all_features, space_id=None))
async def get_all_tabular(parcellation_id: str, region_id: str, type: Optional[str]=None, func=lambda: []):
    """Get all tabular features"""
    type = str(type) if type else None
    return paginate(
        await func(parcellation_id=parcellation_id, region_id=region_id, type=type)
    )

@router.get("/Tabular/{feature_id:lazy_path}", response_model=TabularModels)
@version(*FASTAPI_VERSION)
@wrap_feature_category("Tabular")
@async_router_decorator(ROLE, func=partial(single_feature, space_id=None))
async def get_single_tabular(parcellation_id: str, region_id: str, feature_id: str, type: Optional[str]=None, func=lambda: None):
    """Get a single tabular feature"""
    type = str(type) if type else None
    return await func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, type=type)


# VOI
@router.get("/Image", response_model=Page[SiibraVoiModel])
@version(*FASTAPI_VERSION)
@wrap_feature_category("Image")
@async_router_decorator(ROLE, func=partial(all_features, parcellation_id=None, region_id=None))
async def get_all_voi(space_id: str, bbox: Optional[str]=None, type: Optional[str]=None, func=lambda: []):
    """Get all Image features"""
    type = str(type) if type else None
    return paginate(
        await func(space_id=space_id, type=type, bbox=bbox)
    )

@router.get("/Image/{feature_id:lazy_path}", response_model=SiibraVoiModel)
@version(*FASTAPI_VERSION)
@wrap_feature_category("Image")
@async_router_decorator(ROLE, func=partial(single_feature, parcellation_id=None, region_id=None))
async def get_single_voi(space_id: str, feature_id: str, type: Optional[str]=None, func=lambda: []):
    """Get a single Image feature"""
    type = str(type) if type else None
    return await func(space_id=space_id, feature_id=feature_id, type=type)


# GeneExpression
@router.get("/GeneExpressions", response_model=Page[SiibraTabularModel])
@version(*FASTAPI_VERSION)
@wrap_feature_category("GeneExpressions")
@async_router_decorator(ROLE, func=partial(all_features, space_id=None, type="GeneExpressions"))
async def get_all_gene(parcellation_id: str, region_id: str, gene: str, func=lambda: []):
    """Get all GeneExpressions features"""
    return paginate(
        await func(parcellation_id=parcellation_id, region_id=region_id, gene=gene)
    )

@router.get("/GeneExpressions/{feature_id:lazy_path}", response_model=Page[SiibraTabularModel])
@version(*FASTAPI_VERSION)
@wrap_feature_category("GeneExpressions")
@async_router_decorator(ROLE, func=partial(single_feature, space_id=None, type="GeneExpressions"))
async def get_single_gene(parcellation_id: str, region_id: str, feature_id: str, gene: str, func=lambda: []):
    """Get a single GeneExpressions feature"""
    return await func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, gene=gene)


# EbrainsDataFeature
@router.get("/EbrainsDataFeature", response_model=Page[SiibraEbrainsDataFeatureModel])
@version(*FASTAPI_VERSION)
@wrap_feature_category("EbrainsDataFeature")
@async_router_decorator(ROLE, func=partial(all_features, space_id=None, type="EbrainsDataFeature"))
async def get_all_ebrains_df(parcellation_id: str, region_id: str, func=lambda: []):
    """Get all EbrainsDataFeatures"""
    return paginate(
        await func(parcellation_id=parcellation_id, region_id=region_id)
    )

@router.get("/EbrainsDataFeature/{feature_id:lazy_path}", response_model=Page[SiibraEbrainsDataFeatureModel])
@version(*FASTAPI_VERSION)
@wrap_feature_category("EbrainsDataFeature")
@async_router_decorator(ROLE, func=partial(single_feature, space_id=None, type="EbrainsDataFeature"))
async def get_single_ebrains_df(parcellation_id: str, region_id: str, feature_id: str, func=lambda: None):
    """Get a single EbrainsDataFeature"""
    return await func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id)



# n.b. this Union *must* go from more specific to less specific
# TODO figure out how to enforce this (?)
FeatureIdResponseModel = Union[
    SiibraVoiModel,
    CortialProfileModels,
    RegionalConnectivityModels,
    TabularModels,
    SiibraTabularModel,
    SiibraEbrainsDataFeatureModel,
]
@router.get("/{feature_id:lazy_path}", response_model=FeatureIdResponseModel, tags=TAGS, description="""
This endpoint allows detail of a single feature to be fetched, without the necessary context. However, the tradeoff for this endpoint is:

- the endpoint typing is the union of all possible return types
- the client needs to supply any necessary query param (e.g. subject for regional connectivity, gene for gene expression etc)
""")
@version(*FASTAPI_VERSION)
@async_router_decorator(ROLE, func=get_single_feature_from_id)
async def get_single_feature(feature_id: str, request: Request, func):
    """Get a single feature, from feature_id"""
    if not func:
        raise HTTPException(500, detail="get_single_feature, func not passed along")
    try:
        return await func(feature_id=feature_id, **dict(request.query_params))
    except Exception as e:
        raise HTTPException(400, detail=str(e))

class PlotlyTemplate(Enum):
    plotly="plotly"
    plotly_white="plotly_white"
    plotly_dark="plotly_dark"
    ggplot2="ggplot2"
    seaborn="seaborn"
    simple_white="simple_white"
    none="none"


@router.get("/{feature_id:lazy_path}/plotly", description="""
Get the plotly specification of the plot.
            
For the appearance of the template, see [https://plotly.com/python/templates/](https://plotly.com/python/templates/)
""")
@async_router_decorator(ROLE, func=get_single_feature_plot_from_id)
async def get_single_feature_plot(feature_id: str, request: Request, func, template: PlotlyTemplate=PlotlyTemplate.plotly):
    """Get plotly spec from feature_id"""
    try:
        kwargs = {**dict(request.query_params), 'template': template.value if isinstance(template, PlotlyTemplate) else template}
        return await func(feature_id=feature_id, **kwargs)
    except NotFound as e:
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
