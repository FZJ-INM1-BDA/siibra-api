
from fastapi_pagination import paginate, Page
from fastapi_versioning import version
from fastapi.exceptions import HTTPException
from fastapi import Request

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.common import router_decorator
from api.common.data_handlers.features.types import all_feature_types, all_features, single_feature, get_single_feature_from_id
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

from .util import router, wrap_feature_type, wrap_feature_catetory, TAGS

from typing import Union, Optional
from functools import partial
from enum import Enum


@router.get("/_types", response_model=Page[str])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_feature_types)
def get_all_feature_types(func):
    all_types = func()
    all_types.sort()
    return paginate(all_types)


# Regional Connectivity
RegionalConnectivityModels = SiibraRegionalConnectivityModel
class ConnectivityTypes(Enum):
    FunctionalConnectivity="FunctionalConnectivity"
    StreamlineCounts="StreamlineCounts"
    StreamlineLengths="StreamlineLengths"


@wrap_feature_catetory("RegionalConnectivity", path="", response_model=Page[RegionalConnectivityModels], func=partial(all_features, space_id=None, region_id=None))
def get_all_connectivity_features(parcellation_id: str, type: Optional[ConnectivityTypes]=None, func=lambda:[]):
    return paginate(
        func(parcellation_id=parcellation_id, type=str(type))
    )
@wrap_feature_catetory("RegionalConnectivity", path="/{feature_id:lazy_path}", response_model=RegionalConnectivityModels, func=partial(single_feature, space_id=None, region_id=None))
def get_single_connectivity_feature(parcellation_id: str, feature_id: str, subject: str, type: Optional[ConnectivityTypes]=None, func=lambda:None):
    return func(parcellation_id=parcellation_id, feature_id=feature_id, subject=subject, type=str(type))



# Cortical Profiles
CortialProfileModels = SiibraCorticalProfileModel
class CorticalProfileTypes(Enum):
    ReceptorDensityProfile="ReceptorDensityProfile"
    CellDensityProfile="CellDensityProfile"
    BigBrainIntensityProfile="BigBrainIntensityProfile"

@wrap_feature_catetory("CorticalProfile", path="", response_model=Page[CortialProfileModels], func=partial(all_features, space_id=None))
def get_all_connectivity_features(parcellation_id: str, region_id: str, type: Optional[CorticalProfileTypes]=None, func=lambda:[]):
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id, type=str(type))
    )
@wrap_feature_catetory("CorticalProfile", path="/{feature_id:lazy_path}", response_model=CortialProfileModels, func=partial(single_feature, space_id=None))
def get_single_connectivity_feature(parcellation_id: str, region_id: str, feature_id: str, type: Optional[CorticalProfileTypes]=None, func=lambda:None):
    return func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, type=str(type))



# Tabular
TabularModels = Union[SiibraCorticalProfileModel, SiibraReceptorDensityFp, SiibraTabularModel]

class TabularTypes(Enum):
    ReceptorDensityFingerprint="ReceptorDensityFingerprint"
    LayerwiseBigBrainIntensities="LayerwiseBigBrainIntensities"
    LayerwiseCellDensity="LayerwiseCellDensity"

@wrap_feature_catetory("Tabular", path="", response_model=Page[TabularModels], func=partial(all_features, space_id=None, region_id=None))
def get_all_tabular(parcellation_id: str, region_id: str, type: Optional[TabularTypes]=None, func=lambda: []):
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id, type=str(type))
    )
@wrap_feature_catetory("Tabular", path="/{feature_id:lazy_path}", response_model=TabularModels, func=partial(single_feature, space_id=None, region_id=None))
def get_single_tabular(parcellation_id: str, region_id: str, feature_id: str, type: Optional[TabularTypes]=None, func=lambda: None):
    return func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, type=str(type))



# VOI
@wrap_feature_type("VolumeOfInterest", path="", response_model=Page[SiibraVoiModel], func=partial(all_features, parcellation_id=None, region_id=None))
def get_all_voi(space_id: str, bbox: Optional[str]=None, func=lambda: []):
    return paginate(
        func(space_id=space_id)
    )
@wrap_feature_type("VolumeOfInterest", path="/{feature_id:lazy_path}", response_model=SiibraVoiModel, func=partial(single_feature, parcellation_id=None, region_id=None))
def get_single_voi(space_id: str, feature_id: str, bbox: Optional[str]=None, func=lambda: []):
    return func(space_id=space_id, feature_id=feature_id)



# GeneExpression
@wrap_feature_type("GeneExpressions", path="", response_model=Page[SiibraTabularModel], func=partial(all_features, space_id=None))
def get_all_gene(parcellation_id: str, region_id: str, gene: str, func=lambda: []):
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id, gene=gene)
    )
@wrap_feature_type("GeneExpressions", path="/{feature_id:lazy_path}", response_model=SiibraTabularModel, func=partial(single_feature, space_id=None))
def get_all_gene(parcellation_id: str, region_id: str, feature_id: str, gene: str, func=lambda: []):
    return func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, gene=gene)


# n.b. this Union *must* go from more specific to less specific
# TODO figure out how to enforce this (?)
FeatureIdResponseModel = Union[
    SiibraVoiModel,
    CortialProfileModels,
    RegionalConnectivityModels,
    TabularModels,
    SiibraTabularModel,
]
@router.get("/{feature_id:lazy_path}", response_model=FeatureIdResponseModel, tags=TAGS, description="""
This endpoint allows detail of a single feature to be fetched, without the necessary context. However, the tradeoff for this endpoint is:

- the endpoint typing is the union of all possible return types
- the client needs to supply any necessary query param (e.g. subject for regional connectivity, gene for gene expression etc)
""")
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_single_feature_from_id)
def get_single_feature(feature_id: str, request: Request, func):
    if not func:
        raise HTTPException(500, detail="get_single_feature, func not passed along")
    try:
        return func(feature_id=feature_id, **dict(request.query_params))
    except Exception as e:
        raise HTTPException(400, detail=str(e))
