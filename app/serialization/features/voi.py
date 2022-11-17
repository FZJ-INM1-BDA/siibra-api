from app.serialization.util import serialize, instance_to_model
from models.features.voi import VOIDataModel
from siibra.features.voi import VolumeOfInterest

@serialize(VolumeOfInterest)
def voi_to_model(voi: VolumeOfInterest, **kwargs) -> VOIDataModel:
    super_model = instance_to_model(voi, skip_classes=(VolumeOfInterest, ), **kwargs)
    super_model_dict = super_model.dict()
    super_model_dict["@type"] = "siibra/features/voi"
    return VOIDataModel(
        location=instance_to_model(voi.location, **kwargs),
        volumes=[instance_to_model(vol, **kwargs) for vol in voi.volumes],
        **super_model_dict,
    )
