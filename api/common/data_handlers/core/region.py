from api.common import data_decorator, get_filename
from api.siibra_api_config import ROLE
from typing import List, Dict

@data_decorator(ROLE)
def all_regions(parcellation_id: str, find:str=None) -> List:
    """Get all regions, categorised under the parcellation specified by `parcellation_id`, optionally filtered by find.
    
    Args:
        parcellation_id: id of the parcellation, under which regions will be fetched
        find: string to search for
    
    Returns:
        List of all serialized regions"""
    import siibra
    from api.serialization.util import instance_to_model
    parc = siibra.parcellations[parcellation_id]
    regions = [r for r in (parc.find(find) if find else parc) ]
    return [instance_to_model(r).dict() for r in regions if r is not parc]

@data_decorator(ROLE)
def single_region(parcellation_id: str, region_id: str, space_id: str=None):
    """Get a single region, categorised under parcellation specified by `parcellation_id`, defined by `region_id`.
    
    If space_id optional parameter is supplied, additional information about the region in the space will also be returned.
    
    Args:
        parcellation_id: id of the parcellation, under which the regions will be fetched
        region_id: lookup id of the region
        space_id: additional information about the region in the provided space
    
    Returns:
        The region, specified by the criteria, serialized."""
    import siibra
    from api.serialization.util import instance_to_model
    
    space = siibra.spaces[space_id] if space_id else None
    return instance_to_model(
        siibra.get_region(parcellation_id, region_id),
        space=space
    ).dict()
