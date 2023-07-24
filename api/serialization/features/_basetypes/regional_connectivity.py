from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import RegionalConnectivity
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel

@serialize(RegionalConnectivity, pass_super_model=True)
def regional_conn_to_model(conn: RegionalConnectivity, subject:str=None, detail:bool=False, super_model_dict={}, **kwargs) -> SiibraRegionalConnectivityModel:
    """Serialize regional connectivity
    
    As serialize.pass_super_model is set to true, the instance will first be serialized according to its superclass of RegionalConnectivity (Feature),
    and passed to this function as super_model_dict. User **should** not supply their own `super_model_dict` kwarg, as it will be ignored.
    
    Args:
        conn: instance of RegionalConnnectivity
        subject: subject to be retrieved, passed directly to RegionalConnectivity.get_matrix. If not supplied, "_average" will be populated
        detail: detail flag. If not supplied, matrices attribute will not be populated
    
    Returns:
        SiibraRegionalConnectivityModel
    """
    return SiibraRegionalConnectivityModel(
        **super_model_dict,
        subjects=conn.subjects,
        cohort=conn.cohort,
        matrices={
            subject if subject else '_average': instance_to_model(conn.get_matrix(subject), detail=detail, **kwargs)
        } if detail else None
    )
