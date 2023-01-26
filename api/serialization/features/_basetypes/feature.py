from api.serialization.util.siibra import Feature
from api.serialization.util import serialize, instance_to_model
from api.models.features._basetypes.feature import FeatureModel

@serialize(Feature)
def feature_to_model(feat: Feature, **kwargs):
    return FeatureModel(
        id=feat.id,
        name=feat.name,
        modality=feat.modality,
        description=feat.description,
        # TODO
        # hcp streamline kg id issue.
        # revert when resolved
        datasets=[] #[instance_to_model(ds, **kwargs) for ds in feat.datasets]
    )
