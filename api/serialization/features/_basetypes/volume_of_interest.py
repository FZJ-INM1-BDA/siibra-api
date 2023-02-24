from api.serialization.util.siibra import (
    Image, Feature, Volume
)
from api.models.features._basetypes.volume_of_interest import SiibraVoiModel
from api.serialization.util import (
    serialize,
    instance_to_model
)

# serializing voi is... somewhat complicated, so doing it manually
@serialize(Image, pass_super_model=False)
def voi_to_model(feat: Image, **kwargs):
    feature_super_model = instance_to_model(feat, use_class=Feature)
    volume_super_model = instance_to_model(feat, use_class=Volume)

    feature_dict = feature_super_model.dict()
    feature_dict.pop("@type", None)
    return SiibraVoiModel(
        **feature_dict,
        volume=volume_super_model,
        boundingbox=instance_to_model(feat.boundingbox),
    )
