from api.common import data_decorator
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_atlases():
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(atlas).dict() for atlas in siibra.atlases]

@data_decorator(ROLE)
def single_atlas(atlas_id: str):
    import siibra
    from api.serialization.util import instance_to_model
    atlas = siibra.atlases[atlas_id]
    return instance_to_model(atlas).dict()
