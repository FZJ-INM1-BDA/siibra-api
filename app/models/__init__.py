from typing import Callable, Dict
from pydantic import BaseModel, Field

class HrefModel(BaseModel):
    href: str

class RestfulModel(BaseModel):
    links: Dict[str, HrefModel]

    def __init__(self, get_href_func: Callable[..., Dict[str, HrefModel]]=None, **kwargs):
        if get_href_func:
            kwargs["links"] = get_href_func()
        super().__init__(**kwargs)

