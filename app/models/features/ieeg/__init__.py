from pydantic import Field
from typing import Dict, Optional

from siibra.features.feature import SpatialFeature
from siibra.core import AtlasConcept
from siibra.features.ieeg import IEEG_Session, IEEG_Electrode, IEEG_ContactPoint

from app.models.util import serialize
from app.models.openminds.base import ConfigBaseModel
from app.models.core.datasets import DatasetJsonModel
from app.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as CoordinatePointModel,
)


class InRoiModel(ConfigBaseModel):
    in_roi: Optional[bool] = Field(None, alias="inRoi")

    def process_in_roi(
        self, sf: SpatialFeature, detail=False, roi: AtlasConcept = None, **kwargs
    ):
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

@serialize(IEEG_Session)
def ieegsession_to_model(session: IEEG_Session, **kwargs) -> IEEGSessionModel:
    from app.models import instance_to_model
    dataset = instance_to_model(session.dataset, **kwargs)
    model = IEEGSessionModel(
        id=session.id,
        type="siibra/features/ieegSession",
        dataset=dataset,
        sub_id=session.sub_id,
        electrodes={
            key: instance_to_model(electrode, **kwargs)
            for key, electrode in session.electrodes.items()
        },
    )
    model.process_in_roi(session, **kwargs)
    return model

@serialize(IEEG_Electrode)
def ieegelectrode_to_model(electrode: IEEG_Electrode, **kwargs) -> IEEGElectrodeModel:
    from app.models import instance_to_model
    model = IEEGElectrodeModel(
        electrode_id=electrode.electrode_id,
        contact_points={
            key: instance_to_model(contact_pt, **kwargs)
            for key, contact_pt in electrode.contact_points.items()
        },
    )
    model.process_in_roi(electrode, **kwargs)
    return model

@serialize(IEEG_ContactPoint)
def ieegcontactpt_to_model(ctpt: IEEG_ContactPoint, **kwargs) -> IEEGContactPointModel:
    from app.models import instance_to_model
    model = IEEGContactPointModel(
        id=ctpt.id,
        point=instance_to_model(ctpt.point, **kwargs)
    )
    model.process_in_roi(ctpt, **kwargs)
    return model
