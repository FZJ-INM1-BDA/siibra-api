from typing import Literal, List

from new_api.v3.serialization import instance_to_model
from new_api.common.exceptions import NotFound
from new_api.common.decorators import data_decorator
from new_api.siibra_api_config import ROLE
from new_api.common.logger import logger

from new_api.warmup import register_warmup_fn

@data_decorator(ROLE)
def assign(parcellation_id: str, space_id: str, point: str, assignment_type: str=Literal["statistical", "labelled"], sigma_mm: float=0., extra_specs: str=""):
    import siibra
    from siibra.attributes.locations.point import parse_coordinate, Point
    coordinate = parse_coordinate(point)
    point = Point(coordinate=coordinate, space_id=space_id, sigma=sigma_mm)
    maps = siibra.find_maps(parcellation_id, space_id, assignment_type, extra_specs)
    if len(maps) == 0:
        raise NotFound(f"map with {parcellation_id=!r}, {space_id=!r}, {assignment_type=!r}, {extra_specs=!r} not found")
    mp = maps[0]
    result = mp.lookup_points(point)
    return instance_to_model(result, detail=True).dict()

@register_warmup_fn()
def warmup_maps():
    import siibra
    from siibra.atlases.sparsemap import SparseMap
    maps: List[SparseMap] = siibra.find_maps(maptype="statistical")
    for map in maps:
        try:
            map._get_readable_sparseindex(warmup=True)
        except Exception as e:
            logger.warning(f"Failed to save sparseindex: {str(e)}")

