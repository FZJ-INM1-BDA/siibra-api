from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    Tabular
)
from api.models.features._basetypes.tabular import (
    SiibraTabularModel
)

@serialize(Tabular, pass_super_model=True)
def tabular_to_model(tabular: Tabular, detail=False, super_model_dict={}, **kwargs):
    return SiibraTabularModel(
        **super_model_dict,
        data=instance_to_model(tabular.data, detail=detail, **kwargs) if detail else None
    )
