siibra v0.5 introduced compound features. New serialization strategies and models need to be introduced in order to take full advantage of the introduction of compound features.

## Import the new class

`api.serialization.util.siibra` Serves as the one and single entrypoint to siibra package. To access the new class `CompoundFeature`, import it here.

```python
# in api.serialization.util.siibra

# ... trimmed for brevity

from siibra.feature.feature import CompoundFeature
```

## Adding serialization model

Next, we define the shape of serialized instances of `CompoundFeature`.

Since `CompoundFeature` subclasses `Feature`, it is quite natural to have the model, `CompoundFeatureModel`, subclass `FeatureModel`. 

Here, we also added the property `subfeature_keys`, which is the additional property of `CompoundFeatureModel` compared to `FeatureModel` see [more detail](../api.models/#api.models._commons.ConfigBaseModel.__init_subclass__)

```python
# in api.models.features._basetypes.feature

# ... trimmed for brevity

class CompoundFeatureModel(_FeatureModel, type="compound_feature"):
    """CompoundFeatureModel"""
    subfeature_keys: List[str]

```

## Adding serialization strategy

We then add the logic of serialization.

```python
# in api.serialization.features.feature

from api.serialization.util.siibra import CompoundFeature
from api.models.features._basetypes.feature import CompoundFeatureModel

from api.serialization.util import (
    serialize,
    instance_to_model
)

@serialize(CompoundFeature, pass_super_model=True)
def serialize_cf(cf: CompoundFeature, detail=False, super_model_dict={}, **kwargs) -> CompoundFeatureModel:
    return CompoundFeatureModel(
        **super_model_dict,
        subfeature_keys=cf.subfeature_keys
    )

```

## Testing the added feature

[start the developer server](./develop.md), and try to fetch a new feature.
