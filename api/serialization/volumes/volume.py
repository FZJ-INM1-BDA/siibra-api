from api.serialization.util import serialize, instance_to_model
from api.models.volumes.volume import (
    VolumeModel,
    SiibraAtIdModel
)
from api.serialization.util.siibra import Volume
from api.siibra_api_config import SIIBRA_API_REMAP_PROVIDERS
from typing import Dict, Union
import copy

# recursively remap provider url
# n.b. this function mutates the original dict
# i.e. only pass a deep copy
def remap_provider(obj: Dict[str, Union[dict, str]]):
    if len(SIIBRA_API_REMAP_PROVIDERS) == 0:
        return obj
    for key, value in obj.items():
        if isinstance(value, str):
            for from_host, to_host in SIIBRA_API_REMAP_PROVIDERS.items():
                obj[key] = value.replace(from_host, to_host)
        if isinstance(value, dict):
            remap_provider(value)
    

@serialize(Volume)
def volume_to_model(vol: Volume, **kwargs) -> VolumeModel:
    copied_prov = copy.copy(vol.providers)
    remap_provider(copied_prov)
    
    return VolumeModel(
        name=str(vol.name),
        formats=list(vol.formats),
        provides_mesh=vol.provides_mesh,
        provides_image=vol.provides_image,
        fragments=vol.fragments,
        variant=vol.variant,
        provided_volumes=copied_prov,
        space=SiibraAtIdModel(id=vol.space.id),
        datasets=instance_to_model(vol.datasets, **kwargs)
    )
