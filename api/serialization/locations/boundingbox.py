from api.models.locations.boundingbox import BoundingBoxModel
from api.serialization.util.siibra import Space, BoundingBox, Point
from api.serialization.util import serialize, instance_to_model

@serialize(BoundingBox, pass_super_model=True)
def boundingbox_to_model(bbox: BoundingBox, super_model_dict={}, **kwargs) -> BoundingBoxModel:
    """Serialize BoundingBox instance
    
    Args:
        bbox: instance of bounding box
    
    Returns:
        BoundingBoxModel
    """
    return BoundingBoxModel(
        **super_model_dict,
        id=bbox.id,
        center=instance_to_model(bbox.center, **kwargs),
        minpoint=instance_to_model(bbox.minpoint, **kwargs),
        maxpoint=instance_to_model(bbox.maxpoint, **kwargs),
        shape=bbox.shape,
        is_planar=bbox.is_planar,
    )
