from app.serialization.util import serialize, instance_to_model
from models.features.ieeg import (
    IEEGContactPointModel,
    IEEGSessionModel,
    IEEGElectrodeModel,
)
from siibra.features.ieeg import (
    IEEG_Session,
    IEEG_ContactPoint,
    IEEG_Electrode,
)

@serialize(IEEG_Session)
def ieegsession_to_model(session: IEEG_Session, **kwargs) -> IEEGSessionModel:
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
    model = IEEGContactPointModel(
        id=ctpt.id,
        point=instance_to_model(ctpt.point, **kwargs)
    )
    model.process_in_roi(ctpt, **kwargs)
    return model
