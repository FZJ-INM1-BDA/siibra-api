from api.common import data_decorator
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def all_parcellations():
    """Get all parcellations
    
    Returns:
        List of all serialized parcellations"""
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(parc).dict() for parc in siibra.parcellations]

@data_decorator(ROLE)
def single_parcellation(parc_id: str):
    """Get a single parcellation
    
    Args:
        parc_id: id of the parcellation
    
    Returns:
        The parcellation specified by the provided id, serialized into dict
    """
    import siibra
    from api.serialization.util import instance_to_model
    return instance_to_model(
        siibra.parcellations[parc_id]
    ).dict()
