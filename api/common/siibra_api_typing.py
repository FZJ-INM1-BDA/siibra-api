try:
    from typing import Literal, Union
except ImportError:
    from typing import Union
    from typing_extensions import Literal


ROLE_TYPE = Union[Literal['worker'], Literal["server"], Literal["all"]]
