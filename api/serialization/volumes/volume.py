from api.serialization.util import serialize, instance_to_model
from api.models.volumes.volume import (
    VolumeModel,
    SiibraAtIdModel
)
from api.serialization.util.siibra import Volume

@serialize(Volume)
def volume_to_model(vol: Volume, **kwargs) -> VolumeModel:
    return VolumeModel(
        name=str(vol.name),
        formats=list(vol.formats),
        provides_mesh=vol.provides_mesh,
        provides_image=vol.provides_image,
        fragments=vol.fragments,
        variant=vol.variant,
        provided_volumes=vol.providers,
        space=SiibraAtIdModel(id=vol.space.id),
        datasets=instance_to_model(vol.datasets, **kwargs)
    )
