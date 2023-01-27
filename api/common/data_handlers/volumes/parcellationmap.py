from api.common import data_decorator
from api.models.volumes.volume import MapType
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def get_map(parcellation_id: str, space_id: str, maptype: MapType):
    import siibra
    from api.serialization.util import instance_to_model

    # check maptype name and value both matches
    assert maptype.name == maptype.value, f"str enum, expecting .name and .value to equal"
    siibra_maptype = siibra.MapType[maptype.name]
    assert siibra_maptype.name == maptype.name, f"Expecting maptype.name to match"

    return instance_to_model(
        siibra.get_map(parcellation_id, space_id, siibra_maptype)
    ).dict()
