from api.common import data_decorator
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_regions(parcellation_id: str):
    import siibra
    from api.serialization.util import instance_to_model
    parc = siibra.parcellations[parcellation_id]
    return [instance_to_model(r).dict() for r in parc if r is not parc]

@data_decorator(ROLE)
def single_region(parcellation_id: str, region_id: str, space_id: str=None):
    import siibra
    from api.serialization.util import instance_to_model
    
    space = siibra.spaces[space_id] if space_id else None
    return instance_to_model(
        siibra.get_region(parcellation_id, region_id),
        space=space
    ).dict()