siibra v0.5 introduced compound features. New serialization strategies and models need to be introduced in order to take full advantage of the introduction of compound features.

## Import the new class

`api.serialization.util.siibra` Serves as the one and single entrypoint to siibra package. To access the new class `CompoundFeature`, import it here.

```diff
# in api.serialization.util.siibra

# ... trimmed for brevity

+ from siibra.feature.feature import CompoundFeature
```

## Adding serialization model

Next, we define the shape of serialized instances of `CompoundFeature`.

Since `CompoundFeature` subclasses `Feature`, it is quite natural to have the model, `CompoundFeatureModel`, subclass `FeatureModel`. 

Here, we also added the property `subfeature_keys`, which is the additional property of `CompoundFeatureModel` compared to `FeatureModel` see [more detail](../api.models/#api.models._commons.ConfigBaseModel.__init_subclass__)

```diff
# in api.models.features._basetypes.feature

# ... trimmed for brevity

from api.models.features.anchor import SiibraAnchorModel
- from typing import List, Optional
+ from api.models.locations.point import CoordinatePointModel
+ from typing import List, Optional, Union
from abc import ABC

# ... trimmed for brevity


+ class SubfeatureModel(ConfigBaseModel):
+     id: str
+     index: Union[str, CoordinatePointModel]
+     name: str
+ 
+ class CompoundFeatureModel(_FeatureModel, type="compoundfeature"):
+     indices: List[SubfeatureModel]
```

## Adding serialization strategy

We then add the logic of serialization.

```diff
# in api.serialization.features.feature

# ... trimmed for brevity

- from api.serialization.util.siibra import Feature
+ from api.serialization.util.siibra import Feature, CompoundFeature
from api.serialization.util import serialize, instance_to_model
- from api.models.features._basetypes.feature import FeatureModel
+ from api.models.features._basetypes.feature import FeatureModel, CompoundFeatureModel, SubfeatureModel
+ 
+ @serialize(CompoundFeature, pass_super_model=True)
+ def cmpdfeature_to_model(cf: CompoundFeature, detail: bool=False, super_model_dict={}, **kwargs):
+     return CompoundFeatureModel(
+         **super_model_dict,
+         indices=[SubfeatureModel(id=ft.id, index=instance_to_model(idx), name=ft.name) for (idx, ft) in zip(cf.indices, cf.elements)]
+     )
+ 


```

## Updating response models

Whilst the update to serve compound feature does not require the addition of additional REST endpoints, several existing endpoints needs to be updated, as their response would contain compound feature model *in addition* to the previous models.

```diff
# api.server.features.__init__

# ... trimmed for brevity

+ from api.models.features._basetypes.feature import (
+     CompoundFeatureModel
+ )

# ... trimmed for brevity

# Regional Connectivity
- RegionalConnectivityModels = SiibraRegionalConnectivityModel
+ RegionalConnectivityModels = Union[SiibraRegionalConnectivityModel, CompoundFeatureModel]

# ... trimmed for brevity

# Cortical Profiles
- CortialProfileModels = SiibraCorticalProfileModel
+ CortialProfileModels = Union[SiibraCorticalProfileModel, CompoundFeatureModel]

# ... trimmed for brevity

# Tabular
- TabularModels = Union[SiibraCorticalProfileModel, SiibraReceptorDensityFp, SiibraTabularModel]
+ TabularModels = Union[CompoundFeatureModel, SiibraCorticalProfileModel, SiibraReceptorDensityFp, SiibraTabularModel]


```

## Testing the added feature

[start the developer server](./develop.md), and try to fetch a new feature.
