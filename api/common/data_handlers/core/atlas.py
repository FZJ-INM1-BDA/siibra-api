from api.common import data_decorator
from api.siibra_api_config import ROLE
from typing import List, Dict

@data_decorator(ROLE)
def all_atlases() -> List[Dict]:
    """Get all atlases
    
    Returns:
        List of all serialized atlases."""
    import siibra
    from api.serialization.util import instance_to_model
    return [instance_to_model(atlas).dict() for atlas in siibra.atlases]

@data_decorator(ROLE)
def single_atlas(atlas_id: str) -> Dict:
    """Get a single atlas
    
    Args:
        atlas_id: id of the atlas

    Returns:
        The atlas specified by the provided id, serialized into dict
    """
    import siibra
    from api.serialization.util import instance_to_model
    atlas = siibra.atlases[atlas_id]
    return instance_to_model(atlas).dict()
