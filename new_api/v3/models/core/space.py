from new_api.v3.models._commons import ConfigBaseModel
from new_api.v3.models.volumes.volume import VolumeModel
from new_api.v3.models.openminds.SANDS.v3.atlas.commonCoordinateSpace import (
    Model as _CommonCoordinateSpaceModel,
    AxesOrigin,
)
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel
from typing import List, Optional
from pydantic import Field

class CommonCoordinateSpaceModel(_CommonCoordinateSpaceModel, ConfigBaseModel, type="space"):
    """
    CommonCoordinateSpaceModel. Whilst the concept of a coordinate space does not necessitate the existence of an image, in practice, every coordinate space is associated with an image (either volumetric or , in the case of fsaverage, surface-based).
    The origin of the coordinate space is determined by the original data (e.g. affine header in NifTI). All spaces are in RAS neuroanatomical convention.
    """
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

