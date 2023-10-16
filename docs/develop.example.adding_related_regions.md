siibra-0.4a74 introduced `get_related_regions` instance method for `Region` objects. This guide demonstrates how a new endpoint is added to accomodate this new feature.

## Import the new class

`api.serialization.util.siibra` Serves as the one and only entrypoint to siibra package. To access the new class `RegionRelationAssessments`, import it here.

```diff
# in api.serialization.util.siibra

- from siibra.core.region import Region
+ from siibra.core.region import Region, RegionRelationAssessments
```

## Adding serialization model

Next, the model of serialized `RegionRelationAssessments` is defined. 

```diff
# in api.models.core.region

+ from api.models.core.parcellation import SiibraParcellationModel
+ from enum import Enum

+ class Qualification(str, Enum):
+     EXACT = "EXACT"
+     OVERLAPS = "OVERLAPS"
+     CONTAINED = "CONTAINED"
+     CONTAINS = "CONTAINS"
+     APPROXIMATE = "APPROXIMATE"
+     HOMOLOGOUS = "HOMOLOGOUS"
+     OTHER_VERSION = "OTHER_VERSION"

+ class RegionRelationAsmtModel(ConfigBaseModel, type="regionRelationAssessment"):
+    qualification: Qualification
+    query_structure: ParcellationEntityVersionModel
+    assigned_structure: ParcellationEntityVersionModel
+    assigned_structure_parcellation: SiibraParcellationModel

```

Note that `Qualificaiton` Enum is mirrored from `siibra.core.relation_quantification.Quantification`. The duplication is necessary, since the `models` module cannot import `siibra`.

## Adding serialization logic

Now, logic of how to serialize `RegionalRelationshipAsessment` instance to `RegionRelationAsmtModel` will be written

```diff
# api.serialization.core.region
from api.models.core.region (
    ParcellationEntityVersionModel,
    HasAnnotation,
    Coordinates,
    BestViewPoint,
+    RegionRelationAsmtModel,
)
from api.serialization.util import (
    serialize,
    REGISTER,
+    instance_to_model
)
- from api.serialization.util.siibra import Region, Space, parcellations
+ from api.serialization.util.siibra import Region, Space, parcellations, RegionRelationAssessments

# ... truncated for brevity

+@serialize(RegionRelationAssessments)
+def region_relation_ass_to_model(ass: +RegionRelationAssessments, detail=False, **kwargs):
+
+    qualification = ass.qualification
+    assigned_structure = ass.assigned_structure
+    assigned_structure_parcellation = assigned_structure_parcellation
+
+    return RegionRelationAsmtModel(
+        qualification=qualification.name,
+        assigned_structure=instance_to_model(assigned_structure, detail=False, **kwargs),
+        assigned_structure_parcellation=instance_to_model(assigned_structure_parcellation, detail=False, **kwargs),
+        query_structure=instance_to_model(ass.query_structure, detail=False, **kwargs)
+    )

```

## Adding query logic

Here, we define, given string primitives, how to retrieve siibra objects. In our case, given `parcellation_id: str` and `region_id: str`, how to get a list of `RegionalRelationshipAsessments`. (The serialization is also done at this step).

```diff
# api.common.data_handlers.core.region

+@data_decorator(ROLE)
+def get_related_regions(parcellation_id: str, region_id: str):
+    """Get related regions, including the relationship qualification.
+    
+    Args:
+        parcellation_id: id of the parcellation, under which the regions will be fetched
+        region_id: lookup id of the region
+    
+    Returns:
+        List of RegionalRelationshipAssessments, serialized"""
+    import siibra
+    from api.serialization.util import instance_to_model
+    
+    region = siibra.get_region(parcellation_id, region_id)
+    
+    return [instance_to_model(ass).dict() for ass in region.get_related_regions()]
+
```

## Adding the route

Finally, add the route to FastAPI

```diff
# api.server.core.region
-from api.models.core.region import ParcellationEntityVersionModel
+from api.models.core.region import ParcellationEntityVersionModel, RegionRelationAsmtModel
-from api.common.data_handlers.core.region import all_regions, single_region
+from api.common.data_handlers.core.region import all_regions, single_region, get_related_regions

# ... truncated for brevity

+@router.get("/{region_id:lazy_path}/related", response_model=Page[RegionRelationAsmtModel])
+@version(*FASTAPI_VERSION)
+@router_decorator(ROLE, func=get_related_regions)
+def get_related_region(parcellation_id: str, region_id: str, func=lambda:[]):
+    """HTTP get_related_regions of the specified region"""
+    return paginate(
+        func(parcellation_id=parcellation_id, region_id=region_id)
+    )
    
```

## Manual Test

To test that what we added works, we try to query something that we know will yield a positive result. According to [siibra-python e2e test](https://github.com/FZJ-INM1-BDA/siibra-python/commit/0b5c68de3e69e569e4f3e17b2c1c6e9e8030b244), parcellation id of `2.9` and region spec of `PGa` should yield results for both `OTHER_VERSION` and `HOMOLOGOUS`. 

First, we start a local dev server with:

```bash
uvcorn api.server:api
```

Then we navigate browser to `http://localhost:8000/v3_0/docs`, finding the newly introduced endpoint listed in the swagger UI under `/regions/{region_id}/related`. We click `Try it out`, and enter `2.9` as `parcellation_id` and `PGa` as `region_id`, and click `Execute`, and we get the result below:

```json
{
    "items": [
        {
            "qualification": "OTHER_VERSION"
            // ... truncated for brevity
        },
        {
            "qualification": "HOMOLOGOUS"
            // ... truncated for brevity
        }
        // ... truncated for brevity
    ],
    "total": 6,
    "page": 1,
    "size": 50,
    "pages": 1
}
```

## Automated tests

To prevent regression, we add the tests to e2e test

```diff
# e2e_test/regions/test_related.py

+import pytest
+from fastapi.testclient import TestClient
+from api.server import api
+
+client = TestClient(api)
+
+@pytest.mark.parametrize("parc, reg_spec, has_related, +has_homology", [
+    ("2.9", "PGa", True, True),
+    ("monkey", "PG", False, True),
+    ("waxholm v3", "cornu ammonis 1", True, False),
+])
+def test_related(parc, reg_spec, has_related, has_homology):
+    response = client.get(f"/v3_0/regions/{reg_spec}/+related", params={
+        "parcellation_id": parc
+    })
+    assert response.status_code == 200
+    resp_json = response.json()
+    items = resp_json.get("items", [])
+    
+    other_versions = [item for item in items if item.get("qualification") == "OTHER_VERSION"]
+    homologous = [item for item in items if item.get("qualification") == "HOMOLOGOUS"]
+    assert (len(other_versions) > 0) == has_related
+    assert (len(homologous) > 0) == has_homology
+
```
