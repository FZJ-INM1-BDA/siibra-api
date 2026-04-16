from typing import Optional

from new_api.common.decorators import data_decorator
from new_api.siibra_api_config import ROLE


@data_decorator(ROLE)
def find_spatial_features(
    space_id: str, bbox: Optional[str] = None, category: str = None
):
    import siibra
    from siibra.commons.logger import logger
    from siibra.attr_collections import FeatureSet
    from new_api.v3.serialization.feature import featureset_to_voi

    logger.setLevel("ERROR")

    return_all_flag = category is None

    fts: list[FeatureSet] = siibra.spatial_query(space_id, bbox)
    result = []
    for ft in fts:
        v = featureset_to_voi(ft, space_id=space_id)
        if not return_all_flag and v.category != category:
            continue

        result.append(v.dict())
    return result
