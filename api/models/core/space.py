from api.models._commons import ConfigBaseModel
from api.models.volumes.volume import VolumeModel
from api.models.openminds.SANDS.v3.atlas.commonCoordinateSpace import (
    Model as _CommonCoordinateSpaceModel,
    AxesOrigin,
)
from api.models._retrieval.datasets import EbrainsDatasetModel
from typing import List, Optional
from pydantic import Field

class CommonCoordinateSpaceModel(_CommonCoordinateSpaceModel, ConfigBaseModel, type="space"):
    """CommonCoordinateSpaceModel"""
    default_image: Optional[List[VolumeModel]] = Field(
        None,
        alias='defaultImage',
        description='Two or three dimensional image that particluarly represents a specific coordinate space. Overriden by Siibra API to use as VolumeModel',
        min_items=1,
        title='defaultImage',
    )
    datasets: Optional[List[EbrainsDatasetModel]] = Field(
        None,
        alias="datasets",
    )
