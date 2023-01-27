
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.common import router_decorator
from api.common.data_handlers.features.types import all_feature_types, all_features, single_feature
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

from .util import router, wrap_feature_type

from typing import Union, Optional
from functools import partial


@router.get("/_types", response_model=Page[str])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_feature_types)
def get_all_feature_types(func):
    all_types = func()
    all_types.sort()
    return paginate(all_types)


# Connectivity features
connectivity_features = [
    ("RegionalConnectivity", SiibraRegionalConnectivityModel),
    ("FunctionalConnectivity", SiibraRegionalConnectivityModel),
    ("StreamlineCounts", SiibraRegionalConnectivityModel),
    ("StreamlineLengths", SiibraRegionalConnectivityModel),
]

for data_feature, Model in connectivity_features:
    @wrap_feature_type(data_feature, path="", response_model=Page[Model], func=partial(all_features, space_id=None, region_id=None), tags=["RegionalConnectivity"])
    def get_all_connectivity_features(parcellation_id: str, func):
        return paginate(
            func(parcellation_id=parcellation_id)
        )
    
    @wrap_feature_type(data_feature, path="/{feature_id:lazy_path}", response_model=Model, func=partial(single_feature, space_id=None, region_id=None), tags=["RegionalConnectivity"])
    def get_single_connectivity_feature(parcellation_id: str, feature_id: str, subject: str, func):
        return func(parcellation_id=parcellation_id, feature_id=feature_id, subject=subject)


# CorticalProfiles
cortical_profile_features = [
    ("CorticalProfile", SiibraCorticalProfileModel),
    ("ReceptorDensityProfile", SiibraCorticalProfileModel),
    ("CellDensityProfile", SiibraCorticalProfileModel),
    ("BigBrainIntensityProfile", SiibraCorticalProfileModel),
]

for data_feature, Model in cortical_profile_features:
    @wrap_feature_type(data_feature, path="", response_model=Page[Model], func=partial(all_features, space_id=None), tags=["CorticalProfile"])
    def get_all_cortical_profiles(parcellation_id: str, region_id: str, func=lambda: []):
        return paginate(
            func(parcellation_id=parcellation_id, region_id=region_id)
        )

    @wrap_feature_type(data_feature, path="/{feature_id:lazy_path}", response_model=Model, func=partial(single_feature, space_id=None), tags=["CorticalProfile"])
    def get_single_cortical_profile(parcellation_id: str, feature_id: str, region_id: str, func=lambda:None):
        return func(parcellation_id=parcellation_id, feature_id=feature_id, region_id=region_id)

# Tabular

tabular_features = [
    ("Tabular", Union[SiibraCorticalProfileModel,SiibraTabularModel]),
    ("ReceptorDensityFingerprint", SiibraReceptorDensityFp),
    ("LayerwiseBigBrainIntensities", SiibraTabularModel),
    ("LayerwiseCellDensity", SiibraTabularModel),
]

for data_feature, Model in tabular_features:
    @wrap_feature_type(data_feature, path="", response_model=Page[Model], func=partial(all_features, space_id=None, region_id=None), tags=["Tabular"])
    def get_all_tabular(parcellation_id: str, region_id: str, func=lambda: []):
        return paginate(
            func(parcellation_id=parcellation_id, region_id=region_id)
        )
    
    @wrap_feature_type(data_feature, path="/{feature_id:lazy_path}", response_model=Model, func=partial(single_feature, space_id=None, region_id=None), tags=["Tabular"])
    def get_single_tabular(parcellation_id: str, region_id: str, feature_id: str, func=lambda: None):
        return func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id)

@wrap_feature_type("VolumeOfInterest", path="", response_model=Page[SiibraVoiModel], func=partial(all_features, parcellation_id=None, region_id=None), tags=["VolumeOfInterest"])
def get_all_voi(space_id: str, bbox: Optional[str]=None, func=lambda: []):
    return paginate(
        func(space_id=space_id)
    )
    
@wrap_feature_type("VolumeOfInterest", path="/{feature_id:lazy_path}", response_model=SiibraVoiModel, func=partial(single_feature, parcellation_id=None, region_id=None), tags=["VolumeOfInterest"])
def get_single_voi(space_id: str, feature_id: str, bbox: Optional[str]=None, func=lambda: []):
    return func(space_id=space_id, feature_id=feature_id)

@wrap_feature_type("GeneExpressions", path="", response_model=Page[SiibraTabularModel], func=partial(all_features, space_id=None), tags=["Tabular"])
def get_all_gene(parcellation_id: str, region_id: str, gene: str, func=lambda: []):
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id, gene=gene)
    )

@wrap_feature_type("GeneExpressions", path="/{feature_id:lazy_path}", response_model=SiibraTabularModel, func=partial(single_feature, space_id=None), tags=["Tabular"])
def get_all_gene(parcellation_id: str, region_id: str, feature_id: str, gene: str, func=lambda: []):
    return func(parcellation_id=parcellation_id, region_id=region_id, feature_id=feature_id, gene=gene)
