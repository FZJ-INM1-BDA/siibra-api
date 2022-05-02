from typing import Callable, ClassVar, Dict, List, Union
from pydantic import BaseModel, Field
from functools import wraps
from siibra.features.connectivity import ConnectivityMatrixDataModel, ConnectivityMatrix
from siibra.core.serializable_concept import JSONSerializable

class HrefModel(BaseModel):
    href: str

class RestfulModel(BaseModel):
    links: Dict[str, HrefModel]
    _decorated_links: ClassVar[Dict[str, str]] = dict()

    @classmethod
    def decorate_link(cls, link_name: str):
        def outer(fn: Callable):
            cls._decorated_links[link_name] = fn.__name__
            @wraps(fn)
            def inner(*args, **kwargs):
                return fn(*args, **kwargs)
            return inner
        return outer
    

    @classmethod
    def create_links(cls, **kwargs) -> Dict[str, 'HrefModel']:
        from ..app import app
        return {
            link_name: HrefModel(href=app.url_path_for(endpoint_fn_name, **kwargs))
            for link_name, endpoint_fn_name in cls._decorated_links.items()
        }

    def __init_subclass__(cls) -> None:
        cls._decorated_links = dict()
        return super().__init_subclass__()

class SerializationErrorModel(BaseModel):
    type: str = Field("spy/serialization-error", const=True)
    message: str

class CustomList(list):

    @staticmethod
    def serialize(instance: JSONSerializable, **kwargs):
        try:
            return instance.to_model(**kwargs)
        except Exception as e:
            return SerializationErrorModel(message=str(e))

    def __init__(self, full_list: List[JSONSerializable], **kwargs):
        self.full_list = full_list
        self.kwargs = kwargs
        super().__init__()

    def __len__(self):
        return len(self.full_list)

    def __getitem__(self, key: Union[int, slice]):
        try:
            of_interest = self.full_list[key]
            if isinstance(of_interest, list):
                return [CustomList.serialize(mod, **self.kwargs) for mod in of_interest]
            return CustomList.serialize(of_interest, **self.kwargs)
        except IndexError as e:
            raise e


SPyParcellationFeature = ConnectivityMatrix

SPyParcellationFeatureModel = Union[ConnectivityMatrixDataModel, SerializationErrorModel]
