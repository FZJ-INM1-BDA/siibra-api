from api.models.volumes.parcellationmap import MapModel
from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import Map
from datetime import date

@serialize(Map, pass_super_model=True)
def map_to_model(map: Map, super_model_dict={}, **kwargs):
    return MapModel(
        **super_model_dict,
        species=str(map.species),
        indices={
            regionname: instance_to_model(mapindex, **kwargs)
            for regionname, mapindex in map._indices.items()
        },
        volumes=[instance_to_model(v, **kwargs) for v in map.volumes],
        # affine=map.affine.tolist()
    )
