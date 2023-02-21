from api.models._commons import SiibraAtIdModel, ConfigBaseModel
from api.models.core._concept import _SiibraAtlasConcept
from api.models._commons import MapIndexModel
from api.models.volumes.volume import VolumeModel
from typing import List, Dict

class MapModel(_SiibraAtlasConcept):
    species: str
    indices: Dict[str, List[MapIndexModel]]
    volumes: List[VolumeModel]
    # affine: List[float]
    