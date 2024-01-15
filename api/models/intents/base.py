from abc import ABC
from api.models._commons import ConfigBaseModel

class _BaseIntent(ConfigBaseModel, ABC, type="intent"):
    pass
