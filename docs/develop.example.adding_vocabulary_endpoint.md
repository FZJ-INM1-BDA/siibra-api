This document will record the process to reimplement the `/genes` endpoint, which was briefly removed during the refactor of `/v2_0` to `/v3_0`. This should serve as an informative document, the process adds a top level module, which needs to be included for the server/worker architecture to work properly.

## Adding the new import

`api.serialization.util.siibra` Serves as the one and single entrypoint to siibra package. To access the new variable `GENE_NAMES`, import it here.

```diff
# in api.serialization.util.siibra

# ... trimmed for brevity

+ from siibra.vocabularies import GENE_NAMES
```

## Adding serialization model

Next, we define the shape of serialized instance of gene. As this is the first model to be added in vocabulary module, it is useful to add the base class for vocabulary.

```diff
# api.models.vocabularies.__init__
```

```diff
# api.models.vocabularies.base
+ from api.models._commons import (
+     ConfigBaseModel,
+ )
+ from abc import ABC
+ 
+ class _VocabBaseModel(ConfigBaseModel, ABC, type="vocabulary"):
+     ...

```

```diff
# api.models.vocabularies.gene
+ from .base import _VocabBaseModel
+ 
+ class GeneModel(_VocabBaseModel, type="gene"):
+     symbol: str
+     description: str

```

The advantage of constructing the inheritence model `ConfigBaseModel` -> `_VocabBaseModel` -> `GeneModel` is so that initialized model will automatically have the `@type` attribute set to `siibra-1.0/vocabulary/gene`. 


## Adding serialization strategy

For serializing `GENE_NAMES`, this step can be skipped, as the variable is already a dictionary.

This is, however, a double edged sword. An unshaped dictionary can change the key/shape without warning. More so than ever, adding tests would be crucial to ensure future versions of siibra does not break siibra-api.

## Adding query logic

Here, we define, given arguments as string primitives, how to retrieve siibra objects. In our case, given optional string argument `find`, how to get a list of `GeneModel`.

```diff
# api.common.data_handlers.vocabularies.__init__
+ from . import gene
```

```diff
# api.common.data_handlers.vocabularies.gene
+ from api.common import data_decorator
+ from api.siibra_api_config import ROLE
+ from api.models.vocabularies.genes import GeneModel
+ 
+ @data_decorator(ROLE)
+ def get_genes(find:str=None):
+     """Get all genes
+ 
+     Args:
+         string to find in vocabularies
+     
+     Returns:
+         List of the genes."""
+     from api.serialization.util.siibra import GENE_NAMES
+ 
+     if find == None:
+         return_list = [v for v in GENE_NAMES]
+     else:
+         return_list = GENE_NAMES.find(find)
+ 
+     return [GeneModel(
+         symbol=v.get("symbol"),
+         description=v.get("description")
+         ).dict() for v in return_list]

```

Important to note here is, since this is a new module, it *must* be imported into the parent module:

```diff
# api.common.data_handlers.__init__

from . import core
from . import features
from . import volumes
from . import compounds
+ from . import vocabularies

from api.siibra_api_config import ROLE

if ROLE == "all" or ROLE == "worker":
    import siibra
    siibra.warm_cache()

```

## Adding the route

Finally, add the route to FastAPI

```diff
# api.server.vocabularies.__init__
+ from fastapi import APIRouter, HTTPException
+ from fastapi_pagination import paginate, Page
+ from fastapi_versioning import version
+ 
+ from api.server.util import SapiCustomRoute
+ from api.server import FASTAPI_VERSION
+ from api.siibra_api_config import ROLE
+ from api.common import router_decorator
+ from api.models.vocabularies.genes import GeneModel
+ from api.common.data_handlers.vocabularies.gene import get_genes

+ TAGS= ["vocabularies"]
+ """HTTP vocabularies tags"""
+ 
+ router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)
+ """HTTP vocabularies router"""

+ @router.get("/genes", response_model=Page[GeneModel])
+ @version(*FASTAPI_VERSION)
+ @router_decorator(ROLE, func=get_genes)
+ def get_genes(find:str=None, func=None):
+     """HTTP get (filtered) genes"""
+     if func is None:
+         raise HTTPException(500, "func: None passed")
+     return paginate(func(find=find))

```

```diff
# api.server.api

# ... truncated for brevity

from .features import router as feature_router
+ from .volcabularies import router as vocabolaries_router
from .metrics import prom_metrics_resp, on_startup as metrics_on_startup, on_terminate as metrics_on_terminate

# ... truncated for brevity

siibra_api.include_router(feature_router, prefix="/feature")
+ siibra_api.include_router(vocabolaries_router, prefix="/vocabularies")

add_pagination(siibra_api)

# ... truncated for brevity
```

## Configure workers

Since a new top level module was introduced, a new queue is automatically created. New workers must be configured to take jobs from this queue, or HTTP requests related to this queue will hang forever.

```diff
# api.siibra_api_config

# ... truncated for brevity

_queues = [
    "core",
    "features",
    "volumes",
    "compounds",
+    "vocabularies",
]

# ... truncated for brevity

```

```diff
# .helm/siibra-api.values.yaml

# ... truncated for brevity

sapiVersion: "0.3.15" # "latest" or "0.3.15"
- sapiWorkerQueues: ["core", "features", "volumes", "compounds"]
+ sapiWorkerQueues: ["core", "features", "volumes", "compounds", "vocabularies"]
sapiFlavor: "prod" # could be prod, rc, latest, etc

# ... truncated for brevity
```