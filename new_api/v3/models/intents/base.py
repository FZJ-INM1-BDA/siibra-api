from abc import ABC
from new_api.v3.models._commons import ConfigBaseModel

class _BaseIntent(ConfigBaseModel, ABC, type="intent"):
    pass
