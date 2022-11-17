from app.serialization.util import serialize
from siibra.features.feature import RegionalFingerprint, RegionalFeature, Feature, CorticalProfile
import json
from models.features.feature import RegionalFingerprintModel, FPDataModel, CorticalProfileModel

@serialize(Feature)
def f_to_model(f: Feature, **kawrgs):
    
    pass

@serialize(RegionalFeature)
def rf_to_model(rf: RegionalFeature, **kwargs):
    pass

@serialize(RegionalFingerprint)
def fp_to_model(rfp: RegionalFingerprint, *, detail:bool=False, **kwargs) -> RegionalFingerprintModel:
    model = RegionalFingerprintModel(
        description=rfp.description,
        measuretype=rfp.measuretype,
        unit=rfp.unit,
        name=rfp.name,
    )
    if detail is False:
        return model

    dataframe_dict = json.loads(rfp.data.to_json())
    data = FPDataModel(
        mean=dataframe_dict.get("mean", {}),
        std=dataframe_dict.get("std", {}),
    )
    model.data = data
    return model
    
@serialize(CorticalProfile)
def cortprofile_to_model(cortprofile: CorticalProfile, *, detail: bool = False, **kwargs):
    model = CorticalProfileModel(
        description=cortprofile.description,
        measuretype=cortprofile.measuretype,
        unit=cortprofile.unit,
        name=cortprofile.name,
    )
    if detail is False:
        return model
    dataframe_dict = json.loads(cortprofile.data.to_json())
    model.data = dataframe_dict
    return model

