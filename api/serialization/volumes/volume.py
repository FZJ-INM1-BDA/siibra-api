from api.serialization.util import serialize, instance_to_model
from api.models.volumes.volume import (
    VolumeDataModel,
    VolumeModel,
)
from siibra.volumes import VolumeSrc

@serialize(VolumeSrc)
def volume_to_model(vol: VolumeSrc, **kwargs) -> VolumeModel:
    super_model = instance_to_model(vol, skip_classes=(VolumeSrc,), **kwargs)
    super_dict = {
        **super_model.dict(),
        **{"@id": vol.id, "@type": f"spy/volume/{vol.volume_type}"},
    }

    return VolumeModel(
        data=VolumeDataModel(
            type=vol.volume_type,
            is_volume=vol.is_volume,
            is_surface=vol.is_surface,
            detail=vol.detail or {},
            space={"@id": vol.space.id},
            url=vol.url if isinstance(vol.url, str) else None,
            url_map=vol.url if isinstance(vol.url, dict) else None,
            map_type=vol.map_type.name
            if hasattr(vol, "map_type") and vol.map_type is not None
            else None,
            volume_type=vol.volume_type,
        ),
        **super_dict,
    )
