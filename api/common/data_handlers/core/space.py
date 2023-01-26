from api.common import data_decorator
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_spaces():
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(space).dict() for space in siibra.spaces]

@data_decorator(ROLE)
def single_space(space_id: str):
    import siibra
    from api.serialization.util import instance_to_model
    return instance_to_model(
        siibra.spaces[space_id]
    ).dict()
