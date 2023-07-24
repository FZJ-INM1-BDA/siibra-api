from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    Tabular
)
from api.models.features._basetypes.tabular import (
    SiibraTabularModel
)

@serialize(Tabular, pass_super_model=True)
def tabular_to_model(tabular: Tabular, detail: str=False, super_model_dict={}, **kwargs) -> SiibraTabularModel:
    """Fallback serialization of Tabular feature
    
    As serialize.pass_super_model is set to true, the instance will first be serialized according to its superclass of Tabular (Feature),
    and passed to this function as super_model_dict. User **should** not supply their own `super_model_dict` kwarg, as it will be ignored.
    
    Args:
        tabular: instance of tabular data
        detail: detail flag. If unset, will not populate `data` attribute
    
    Returns:
        SiibraTabularModel
    """
    return SiibraTabularModel(
        **super_model_dict,
        data=instance_to_model(tabular.data, detail=detail, **kwargs) if detail else None
    )
