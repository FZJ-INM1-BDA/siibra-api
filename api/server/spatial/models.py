from typing import TypedDict, Optional
from enum import StrEnum, auto

class GeomSvcModel(TypedDict):
    name: str
    source: str
    label: Optional[str]
    
class GeomSvcArtefactEnum(StrEnum):
    ABSENT = auto()
    PRESENT = auto()
    PENDING = auto()
    RUNNING = auto()
    ERROR = auto()
    
class GeomSvcArtefactStatus(TypedDict):
    status: GeomSvcArtefactEnum
    uri: Optional[dict[str, str]]

class SpatialBackendRespModel(TypedDict):
    target_point: list[float]


class SpatialBackendMultiRespModel(TypedDict):
    target_points: list[list[float]]

class SpatialBackendPostModel(TypedDict):
    from_space_id: str
    to_space_id: str
    from_points: list[list[float]]