from pydantic import BaseModel
from typing import Dict, ClassVar, Dict, Callable
from functools import wraps

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
    def create_links(cls, **kwargs) -> Dict[str, "HrefModel"]:
        from app.app import app
        return {
            link_name: HrefModel(href=app.url_path_for(endpoint_fn_name, **kwargs))
            for link_name, endpoint_fn_name in cls._decorated_links.items()
        }

    def __init_subclass__(cls) -> None:
        cls._decorated_links = dict()
        return super().__init_subclass__()

