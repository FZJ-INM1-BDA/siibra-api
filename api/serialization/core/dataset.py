from datetime import date
from api.serialization.util import serialize
from itertools import permutations

from api.models.core.datasets import (
    DatasetVersionModel,
    DatasetJsonModel,
    DATASET_TYPE,
    Url,
)

# # ensure this is decreasing 
# MODEL_TYPE_DICT = {
#     Dataset: DATASET_TYPE
# }

# if len(MODEL_TYPE_DICT) > 1:
#     for (idx0, Cls0), (idx1, Cls1) in permutations(enumerate(MODEL_TYPE_DICT), 2):
#         if issubclass(Cls0, Cls1):
#             assert idx0 < idx1, f"{Cls0} is a subclass of {Cls1}, but is positioned at {idx0}, later than {idx1}."

# @serialize(Dataset)
# def dataset_to_model(ds: Dataset, **kwargs) -> DatasetJsonModel:
    
#     for Cls in MODEL_TYPE_DICT:
#         if isinstance(ds, Cls):
#             model_type = MODEL_TYPE_DICT[Cls]
#             break
#     else:
#         model_type = None
#     metadata = DatasetVersionModel(
#         id=ds.id,
#         type=model_type,
#         accessibility={"@id": ds.embargo_status[0].get("@id")}
#         if hasattr(ds, "embargo_status")
#         and ds.embargo_status is not None
#         and len(ds.embargo_status) == 1
#         else {
#             "@id": "https://openminds.ebrains.eu/instances/productAccessibility/freeAccess"
#         },
#         data_type=[
#             {
#                 "@id": "https://openminds.ebrains.eu/instances/semanticDataType/derivedData"
#             }
#         ],
#         digital_identifier={"@id": None},
#         ethics_assessment={"@id": None},
#         experimental_approach=[{"@id": None}],
#         full_documentation={"@id": None},
#         full_name=ds.name if hasattr(ds, "name") else None,
#         license={"@id": None},
#         release_date=date(1970, 1, 1),
#         short_name=ds.name[:30] if hasattr(ds, "name") else "",
#         technique=[{"@id": None}],
#         version_identifier="",
#         version_innovation="",
#         description=(ds.description or "")[:2000]
#         if hasattr(ds, "description")
#         else "",
#     )
#     return DatasetJsonModel(
#         id=metadata.id,
#         type="https://openminds.ebrains.eu/core/DatasetVersion",
#         metadata=metadata,
#         urls=[Url(**url) for url in ds.urls],
#     )