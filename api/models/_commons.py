from api.models.openminds.base import _BaseModel
from typing import Optional, List, Union, ClassVar, Any
from pydantic import Field

SIIBRA_PYTHON_VERSION = "0.4"

class SiibraAtIdModel(_BaseModel):
    id: str = Field(..., alias="@id")

class ConfigBaseModel(_BaseModel):

    _type: ClassVar[str] = None
    type: Optional[str] = Field(..., alias="@type")

    def __init__(__pydantic_self__, **data) -> None:
        kwargs = {}
        if "type" not in data:
            kwargs["type"] = __pydantic_self__.__class__._type
        super().__init__(**data, **kwargs)


    def __init_subclass__(cls, type=None) -> None:

        # the type should always following the following pattern:
        # siibra-{siibra_python_version}/{generic}/{specific}/{specific+1}...
        # i.e. similar to [MIME types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)
        # this can allow clients to decide on which level of specificity to stop on on parsing the data
        if type:
            if cls._type is None:
                cls._type = f"siibra-{SIIBRA_PYTHON_VERSION}"
            cls._type = f"{cls._type}/{type}"
        
        return super().__init_subclass__()

class MapIndexModel(ConfigBaseModel):
    volume: int
    label: Optional[int]
    fragment: Optional[str]

class SeriesModel(ConfigBaseModel):
    name: Optional[str]
    dtype: str
    index: List[Union[str, int, float]]
    data: List[float]

class DataFrameModel(ConfigBaseModel):
    index: List[Any]
    dtype: str
    columns: List[Any]
    ndim: int
    data: List[List[Union[float, str, List[float]]]]