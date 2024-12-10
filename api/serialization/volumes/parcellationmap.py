from api.models.volumes.parcellationmap import MapModel
from api.models._commons import SiibraAtIdModel
from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import Map

@serialize(Map, pass_super_model=True)
def map_to_model(map: Map, super_model_dict={}, detail=False, **kwargs) -> MapModel:
    """Serialize map instance
    
    Args:
        map: Map instance
    
    Returns:
        MapModel
    """
    return MapModel(
        **super_model_dict,
        species=str(map.species),
        parcellation=SiibraAtIdModel(id=map.parcellation.id),
        space=SiibraAtIdModel(id=map.space.id),
        maptype=map.maptype.name,
        indices={
            regionname: instance_to_model(mapindex, detail=detail, **kwargs)
            for regionname, mapindex in map._indices.items()
        } if detail else {},
        volumes=[instance_to_model(v, detail=detail, **kwargs) for v in map.volumes] if detail else [],
        # affine=map.affine.tolist()
    )
