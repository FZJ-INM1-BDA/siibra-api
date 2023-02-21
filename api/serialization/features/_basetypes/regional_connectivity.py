from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import RegionalConnectivity
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel

@serialize(RegionalConnectivity, pass_super_model=True)
def regional_conn_to_model(conn: RegionalConnectivity, subject=None, detail=False, super_model_dict={}, **kwargs):
    return SiibraRegionalConnectivityModel(
        **super_model_dict,
        subjects=conn.subjects,
        cohort=conn.cohort,
        matrices={
            subject: instance_to_model(conn.get_matrix(subject), detail=detail, **kwargs)
        } if subject and detail else None
    )
