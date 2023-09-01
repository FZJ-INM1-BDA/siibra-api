from . import core
from . import features
from . import volumes
from . import compounds

from ...siibra_api_config import ROLE

if ROLE == "all" or ROLE == "worker":
    import siibra
    siibra.warm_cache()

