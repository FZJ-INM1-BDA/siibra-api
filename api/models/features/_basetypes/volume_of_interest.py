from api.models.features._basetypes.feature import _FeatureModel
from api.models.volumes.volume import VolumeModel
from api.models.locations.boundingbox import BoundingBoxModel

class SiibraVoiModel(_FeatureModel, type="volume_of_interest"):
    volume: VolumeModel
    boundingbox: BoundingBoxModel
