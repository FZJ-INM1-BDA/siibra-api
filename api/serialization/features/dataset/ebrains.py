from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    EbrainsDataFeature, Feature, EbrainsDataset
)
from api.models.features.dataset.ebrains import SiibraEbrainsDataFeatureModel

@serialize(EbrainsDataFeature, pass_super_model=False)
def ebrains_datafeature_to_model(feat: EbrainsDataFeature, detail=False, **kwargs):
    feature_dict = instance_to_model(feat, use_class=Feature, detail=detail, **kwargs).dict()
    feature_dict.pop("datasets", [])
    return SiibraEbrainsDataFeatureModel(
        **feature_dict,
        datasets=[ instance_to_model(feat, use_class=EbrainsDataset) ] if detail else []
    )
