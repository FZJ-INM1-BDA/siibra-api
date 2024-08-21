from api.serialization.util.siibra import Feature
from api.serialization.util import serialize, instance_to_model
from api.models.features._basetypes.feature import FeatureModel

@serialize(Feature)
def feature_to_model(feat: Feature, detail: bool=False, **kwargs) -> FeatureModel:
    """Fallback serialize siibra Feature instance
    
    Args:
        feat: instance of Feature
        detail: require detail flag.
    
    Returns:
        FeatureModel
    """
    return FeatureModel(
        id=feat.id,
        name=feat.name,
        category=feat.category or "Unknown category",
        modality=feat.modality,
        description=feat.description,
        anchor=instance_to_model(feat.anchor, **kwargs) if detail else None,
        datasets=[instance_to_model(ds, **kwargs) for ds in feat.datasets]
    )
