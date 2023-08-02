from api.common import data_decorator
from api.siibra_api_config import ROLE
from typing import Dict, List

@data_decorator(ROLE)
def all_spaces() -> List:
    """Get all spaces
    
    Returns:
        List of all serialized spaces."""
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(space).dict() for space in siibra.spaces]

@data_decorator(ROLE)
def single_space(space_id: str) -> Dict:
    """Get a single space
    
    Args:
        space_id: lookup id of the space
    
    Returns:
        The space specified by the provided id, serialized into Dict"""
    import siibra
    from api.serialization.util import instance_to_model
    return instance_to_model(
        siibra.spaces[space_id]
    ).dict()
