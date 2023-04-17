from api.common import data_decorator, get_filename
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_regions(parcellation_id: str, find:str=None):
    import siibra
    from api.serialization.util import instance_to_model
    parc = siibra.parcellations[parcellation_id]
    regions = [r for r in (parc.find(find) if find else parc) ]
    return [instance_to_model(r).dict() for r in regions if r is not parc]

@data_decorator(ROLE)
def single_region(parcellation_id: str, region_id: str, space_id: str=None):
    import siibra
    from api.serialization.util import instance_to_model
    
    space = siibra.spaces[space_id] if space_id else None
    return instance_to_model(
        siibra.get_region(parcellation_id, region_id),
        space=space
    ).dict()
