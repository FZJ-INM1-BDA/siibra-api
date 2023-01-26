from typing import Optional, Dict, List
from api.models.features._basetypes.feature import FeatureModel
from api.models.volumes.volume import VolumeModel

class SiibraVoiModel(FeatureModel, type="features/_basetype/volume_of_interest"):
    volume: VolumeModel
    