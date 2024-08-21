from new_api.v3.models.openminds.base import _BaseModel
from typing import Optional, List, Union, ClassVar, Any, Literal
from pydantic import Field, BaseModel
from abc import ABC

SIIBRA_PYTHON_VERSION = "2.0"

ignore_cls=(
    "BrainAtlasVersionModel",
    "ParcellationEntityVersionModel",
    "CommonCoordinateSpaceModel",
    "CoordinatePointModel",
)
class SiibraAtIdModel(_BaseModel):
    id: str = Field(..., alias="@id")

class ConfigBaseModel(_BaseModel):
    """ConfigBaseModel"""

    _type: ClassVar[str] = None
    type: Optional[str] = Field(..., alias="@type")

    def __init__(__pydantic_self__, **data) -> None:
        kwargs = {}
        if "type" not in data:
            kwargs["type"] = __pydantic_self__.__class__._type
        super().__init__(**data, **kwargs)

    def __init_subclass__(cls, type: str=None) -> None:
        """On init subclass, configure _type accordingly.

        The type should always following the following pattern:

        ```
        siibra-{siibra_python_version}/{generic}/{specific}/{specific+1}...
        ```

        Similar to [MIME types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)
        This can allow clients to decide on which level of specificity to stop on parsing the data.

        Additionally, fastapi response model type infer is not perfect. 

        e.g.

        ```python
        class B(BaseModel): pass
        class A(B): pass
        response_model = Union[A, B]
        ```
        
        Fastapi will reduce the above will be reduced to `B`.

        To circumvent the problem, all super classes must start with `_`. 

        Since we cannot directly control openminds, we ignore openminds types.

        Args:
            type: type of the new class
        
        Raises:
            AssertionError: if a super class does not start with `_`
            AssertionError: if a super class does not subclass ABC
        """

        if cls.__name__ not in ignore_cls:
            for mro_cls in cls.__mro__[1:]:
                
                # FIXME fastapi does some weird thing when start uvcorn
                if mro_cls.__name__ == cls.__name__:
                    continue

                if mro_cls is ConfigBaseModel:
                    break
                assert mro_cls.__name__[0] == "_", f"{cls.__name__!r} init subclass failure, {mro_cls.__name__!r} is illegal. Subclassed model MUST starts with underscore. Otherwise pydantic may confuse which model to use to serialize."
                assert issubclass(mro_cls, ABC), f"{cls.__name__!r} init subclass failure, {mro_cls.__name__!r} must be subclassed from ABC."
        
        if type:
            if cls._type is None:
                cls._type = f"siibra-{SIIBRA_PYTHON_VERSION}"
            cls._type = f"{cls._type}/{type}"
        
        return super().__init_subclass__()

class MapIndexModel(ConfigBaseModel):
    """MapIndexModel"""
    volume: int
    label: Optional[int]
    fragment: Optional[str]

class SeriesModel(ConfigBaseModel):
    """SeriesModel"""
    name: Optional[str]
    dtype: str
    index: List[Union[str, int, float]]
    data: List[float]

class DataFrameModel(ConfigBaseModel):
    """DataFrameModel"""
    index: List[Any]
    columns: List[Any]
    ndim: int
    data: Optional[
        # to prepare for ndim > 2, maybe we should consider using generic ndim list?
        List[List[
            # probably easier than introducing a dependency to a more generalist module
            Any
            # Optional[Union[float, str, List[float], ParcellationEntityVersionModel]]
        ]]
    ]

class TaskIdResp(BaseModel):
    """TaskIdResp"""
    task_id: str
    status: Optional[
        Union[
            Literal['SUCCESS'],
            Literal['PENDING'],
        ]
    ]
