from api.common import data_decorator, InsufficientParameters, NotFound, AmbiguousParameters
from api.common.logger import logger
from api.siibra_api_config import ROLE, SIIBRA_API_SHARED_DIR
from typing import List, Type, Any, Dict
from hashlib import md5
from pathlib import Path
from zipfile import ZipFile

@data_decorator(ROLE)
def all_feature_types() -> List[Dict[str, str]]:
    """Get all feature types
    
    Returns:
        List of all features, including their name, and inheritance from Feature"""
    from siibra.features import Feature

    
    def get_hierarchy_type(Cls: Type[Any]) -> str:
        """Get inherited class in the form of `Feature.{LessGenericCls}.{SpecificCls}.{Cls}`
        
        Args:
            Cls: subclass of Feature
        
        Returns:
            string representing class hierarchy"""
        return ".".join([
            BaseCls.__name__
            for BaseCls in Cls.__mro__
            if issubclass(BaseCls, Feature)
        ][::-1])

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

@data_decorator(ROLE)
def get_single_feature_plot_from_id(feature_id: str, template="plotly", **kwargs):
    import siibra
    from plotly.io import to_json
    import json

    try:
        feature = siibra.features.Feature.get_instance_by_id(feature_id)
    except Exception as e:
        raise NotFound from e

    try:
        plotly_fig = feature.plot(backend="plotly", template=template)
        json_str = to_json(plotly_fig)
        return json.loads(json_str)

    except NotImplementedError:
        raise NotFound(f"feature with id {feature_id} is found, but the plot function has not been implemented")

@data_decorator(ROLE)
def get_single_feature_download_zip_path(feature_id: str, **kwargs):
    assert feature_id, f"feature_id must be defined"
    hash = md5(feature_id.encode("utf-8"))
    for key, value in kwargs.items():
        hash.update(f"{key}:{value}".encode("utf-8"))
    hex_digest = hash.hexdigest()

    filename = f"fdl-{hex_digest}.zip"
    full_filename = Path(SIIBRA_API_SHARED_DIR, filename)
    if full_filename.is_file():
        return str(full_filename)
    import siibra
    try:
        feat = siibra.features.Feature.get_instance_by_id(feature_id)
    except Exception as e:
        logger.error(f"Error finding single feature {feature_id}, {str(e)}")
        raise NotFound from e
    try:
        feat.export(str(full_filename))
        return str(full_filename)
    except Exception as e:
        logger.error(f"Error export single feature {feature_id}, {str(e)}")
        error_filename = full_filename.with_suffix(".error.zip")
        with ZipFile(error_filename, "w") as zf:
            zf.writestr("error.txt", f"Error exporting file for feature_id: {feature_id}: {str(e)}")
        return str(error_filename)


def extract_concept(*, space_id: str=None, parcellation_id: str=None, region_id: str=None, **kwargs):
    import siibra
    if region_id is not None:
        if parcellation_id is None:
            raise InsufficientParameters(f"if region_id is defined, parcellation_id must also be defined!")
        region: siibra.core.parcellation.region.Region = siibra.get_region(parcellation_id, region_id)
        return region
    
    if parcellation_id:
        parcellation: siibra._parcellation.Parcellation = siibra.parcellations[parcellation_id]
        return parcellation
    
    if space_id:
        space: siibra._space.Space = siibra.spaces[space_id]
        return space
    raise InsufficientParameters(f"concept cannot be extracted")

@data_decorator(ROLE)
def get_all_all_features(*, space_id: str=None, parcellation_id: str=None, region_id: str=None, **kwargs):
    import siibra
    from api.serialization.util import instance_to_model
    concept = extract_concept(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id)
    features = siibra.features.get(concept, siibra.features.Feature)

    re_features = []
    for f in features:
        try:
            re_features.append(
                instance_to_model(f, **kwargs).dict()
            )
        except Exception as e:
            err_str = str(e).replace('\n', ' ')
            logger.warning(f"feature failed to be serialized. Params: space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}. feature id: {f.id}. error: {err_str}")
    return re_features


def _get_all_features(*, space_id: str, parcellation_id: str, region_id: str, type: str, bbox: str=None, **kwargs):
    import siibra
    from siibra.features.image.image import Image
    import json
    if type is None:
        raise InsufficientParameters(f"type is a required kwarg")
    
    # regionalbold cannot be serialized like a normal tabular data
    # feature.data will return error
    banned_list = ("Regional BOLD signal", )

    *_, type = type.split(".")

    concept = extract_concept(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id)
    
    if concept is None:
        raise InsufficientParameters(f"at least one of space_id, parcellation_id and/or region_id must be defined.")
    
    features = [f for f in siibra.features.get(concept, type, **kwargs) if f.modality not in banned_list]

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

    re_features = []
    for f in features:
        try:
            re_features.append(
                instance_to_model(f, detail=False).dict()
            )
        except Exception as e:
            err_str = str(e).replace('\n', ' ')
            logger.warning(f"feature failed to be serialized. Params: space_id={space_id}, parcellation_id={parcellation_id}, region_id={region_id}. feature id: {f.id}, error: {err_str}")
    return re_features


@data_decorator(ROLE)
def single_feature(*, space_id: str, parcellation_id: str, region_id: str, feature_id: str, type: str, **kwargs):
    from api.serialization.util import instance_to_model

    features = _get_all_features(space_id=space_id, parcellation_id=parcellation_id, region_id=region_id, type=type, **kwargs)
    found_feature = [f for f in features if f.id == feature_id]
    return instance_to_model(found_feature[0], detail=True, **kwargs).dict()
