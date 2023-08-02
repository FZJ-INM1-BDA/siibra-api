from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    EbrainsDataFeature, Feature, EbrainsBaseDataset
)
from api.models.features.dataset.ebrains import SiibraEbrainsDataFeatureModel

@serialize(EbrainsDataFeature, pass_super_model=False)
def ebrains_datafeature_to_model(feat: EbrainsDataFeature, detail: str=False, **kwargs) -> SiibraEbrainsDataFeatureModel:
    """Serialize instance of EbrainsDataFeature

    Args:
        feat: instance of EbrainsDataFeature
        detail: detail flag. If unset, `datasets` attribute will be an empty array
    
    Returns:
        SiibraEbrainsDataFeatureModel
    """
    feature_dict = instance_to_model(feat, use_class=Feature, detail=detail, **kwargs).dict()
    feature_dict.pop("datasets", [])
    return SiibraEbrainsDataFeatureModel(
        **feature_dict,
        datasets=[ instance_to_model(feat, use_class=EbrainsBaseDataset) ] if detail else []
    )
