from new_api.v3.models.features._basetypes.feature import _FeatureModel
from new_api.v3.models.volumes.volume import VolumeModel
from new_api.v3.models.locations.boundingbox import BoundingBoxModel

class SiibraVoiModel(_FeatureModel, type="volume_of_interest"):
    """SiibraVoiModel"""
    volume: VolumeModel
    boundingbox: BoundingBoxModel
