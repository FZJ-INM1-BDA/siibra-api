from . import core
from . import features
from . import volumes
from . import compounds
from . import vocabularies

from api.siibra_api_config import ROLE

if ROLE == "all" or ROLE == "worker":
    import siibra
    siibra.warm_cache()

