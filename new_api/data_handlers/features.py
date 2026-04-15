from typing import Optional

from new_api.common.decorators import data_decorator
from new_api.siibra_api_config import ROLE
from new_api.v3.serialization.feature import featureset_to_voi


@data_decorator(ROLE)
def find_spatial_features(space_id: str, bbox: Optional[str] = None):
    import siibra
    from siibra.commons.logger import logger
    from siibra.attr_collections import FeatureSet

    logger.setLevel("ERROR")

    space_spec = {"@id": space_id}

    fts: list[FeatureSet] = siibra.spatial_query(space_id, bbox)
    result = []
    for ft in fts:
        v = featureset_to_voi(ft)
        v.boundingbox.space = space_spec
        v.boundingbox.center.coordinate_space = space_spec
        v.boundingbox.minpoint.coordinate_space = space_spec
        v.boundingbox.maxpoint.coordinate_space = space_spec
        v.volume.space = space_spec
        result.append(v)
    return result
