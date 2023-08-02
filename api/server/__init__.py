"""This module house the HTTP wrapper. Since most call signature and return values
are fastapi standard, they will not be included.

The names of functions will be reflective if their purpose:

- `middleware_*`
- `get_*`
- `exception_*`


"""

from .const import __version__, FASTAPI_VERSION
from .api import siibra_api as api
