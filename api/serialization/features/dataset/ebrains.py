from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    EbrainsDataFeature, Feature, EbrainsBaseDataset
)
from api.models.features.dataset.ebrains import SiibraEbrainsDataFeatureModel

@serialize(EbrainsDataFeature, pass_super_model=True)
def ebrains_datafeature_to_model(feat: EbrainsDataFeature, detail: str=False, super_model_dict={}, **kwargs) -> SiibraEbrainsDataFeatureModel:
    """Serialize instance of EbrainsDataFeature

    Args:
        feat: instance of EbrainsDataFeature
        detail: detail flag. If unset, `datasets` attribute will be an empty array
    
    Returns:
        SiibraEbrainsDataFeatureModel
    """
    return SiibraEbrainsDataFeatureModel(**super_model_dict)
