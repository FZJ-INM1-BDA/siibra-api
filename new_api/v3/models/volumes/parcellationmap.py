from new_api.v3.models._commons import SiibraAtIdModel, ConfigBaseModel
from new_api.v3.models.core._concept import _SiibraAtlasConcept
from new_api.v3.models._commons import MapIndexModel
from new_api.v3.models.volumes.volume import VolumeModel
from typing import List, Dict

class MapModel(_SiibraAtlasConcept):
    """MapModel"""
    species: str
    indices: Dict[str, List[MapIndexModel]]
    volumes: List[VolumeModel]
    # affine: List[float]
    