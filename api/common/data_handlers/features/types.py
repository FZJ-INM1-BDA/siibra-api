from api.common import data_decorator, InsufficientParameters, NotFound, AmbiguousParameters
from api.siibra_api_config import ROLE

def get_hierarchy_type(Cls):
    from siibra.features import Feature
    return ".".join([
        BaseCls.__name__
        for BaseCls in Cls.__mro__
        if issubclass(BaseCls, Feature)
    ][::-1])

@data_decorator(ROLE)
def all_feature_types():
    from siibra.features import Feature
    return [
        {
            'name': get_hierarchy_type(Cls),
            'category': Cls.category,
        } for Cls in Feature.SUBCLASSES
    ]

@data_decorator(ROLE)
def get_single_feature_from_id(feature_id: str, **kwargs):
    import siibra
    from api.serialization.util import instance_to_model
    try:
        feature = siibra.features.Feature.get_instance_by_id(feature_id)
    except Exception as e:
        raise NotFound(str(e))
    else:
        return instance_to_model(feature, detail=True, **kwargs).dict()

def _get_all_features(*, space_id: str, parcellation_id: str, region_id: str, type: str, bbox: str=None, **kwargs):
    import siibra
    from siibra.features.image.image import Image
    import json
    if type is None:
        raise InsufficientParameters(f"type is a required kwarg")
    
    *_, type = type.split(".")

    concept = None
    if region_id is not None:
        if parcellation_id is None:
            raise InsufficientParameters(f"if region_id is defined, parcellation_id must also be defined!")
        concept = siibra.get_region(parcellation_id, region_id)
    
    if concept is None:
        if parcellation_id:
            concept = siibra.parcellations[parcellation_id]
    
    if concept is None:
        if space_id:
            concept = siibra.spaces[space_id]
    
    if concept is None:
        raise InsufficientParameters(f"at least one of space_id, parcellation_id and/or region_id must be defined.")
    
    features = siibra.features.get(concept, type, **kwargs)

    if bbox:
        assert isinstance(concept, siibra.core.space.Space)
        bounding_box = concept.get_bounding_box(*json.loads(bbox))
        features = [f
                for f in features
                if isinstance(f, Image) and
                f.anchor.location.intersects(bounding_box)]

    return features

@data_decorator(ROLE)
def all_features(*, space_id: str, parcellation_id: str, region_id: str, type: str, **kwargs):
    from api.serialization.util import instance_to_model

    features = _get_all_features(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id, type=type, **kwargs)
    return [instance_to_model(f, detail=False).dict() for f in features]

@data_decorator(ROLE)
def single_feature(*, space_id: str, parcellation_id: str, region_id: str, feature_id: str, type: str, **kwargs):
    from api.serialization.util import instance_to_model

    features = _get_all_features(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id, type=type, **kwargs)
    found_feature = [f for f in features if f.id == feature_id]
    return instance_to_model(found_feature[0], detail=True, **kwargs).dict()
