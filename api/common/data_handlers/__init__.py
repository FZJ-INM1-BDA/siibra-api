from . import core
from . import features
from . import volumes
from . import compounds

from ...siibra_api_config import ROLE

if ROLE == "all" or ROLE == "worker":
    try:
        import siibra
        siibra.warm_cache()
    except Exception as e:
        print("Warmup Exception:", e)
