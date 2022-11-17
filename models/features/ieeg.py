from typing import Dict, Optional
from pydantic import Field
from models.openminds.base import ConfigBaseModel
from models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as CoordinatePointModel,
)

from models.core.datasets import DatasetJsonModel


class InRoiModel(ConfigBaseModel):
    in_roi: Optional[bool] = Field(None, alias="inRoi")

    """
    process_in_roi
    Arguments:
    sf: SpatialFeature
    roi: AtlasConcept

    typing is not explicit declared to avoid import of siibra module.
    siibra *is* imported in the function call, since process_in_roi should
    only be called during serialization. During serialization, siibra should
    be a depdency.
    """
    def process_in_roi(
        self, sf, detail=False, roi = None, **kwargs
    ):
        from siibra.features.feature import SpatialFeature
        from siibra.core import AtlasConcept
        assert isinstance(sf, SpatialFeature), f"Expecting sf to be of instance SpatialFeature, but is not"
        if roi:
            assert isinstance(roi, AtlasConcept), f"Expecting roi to be of instance AtlasConcept, but is not"
        
        if not detail:
            return
        if not roi:
            return
        self.in_roi = sf.match(roi)

class IEEGContactPointModel(InRoiModel):
    id: str
    point: CoordinatePointModel


class IEEGElectrodeModel(InRoiModel):
    electrode_id: str
    contact_points: Dict[str, IEEGContactPointModel]

class IEEGSessionModel(InRoiModel):
    id: str = Field(..., alias="@id")
    type: str = Field("siibra/features/ieegSession", alias="@type", const=True)
    dataset: DatasetJsonModel
    sub_id: str
    electrodes: Dict[str, IEEGElectrodeModel]
