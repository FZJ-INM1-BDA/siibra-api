from api.common import data_decorator
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_parcellations():
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(parc).dict() for parc in siibra.parcellations]

@data_decorator(ROLE)
def single_parcellation(parc_id: str):
    import siibra
    from api.serialization.util import instance_to_model
    return instance_to_model(
        siibra.parcellations[parc_id]
    ).dict()
