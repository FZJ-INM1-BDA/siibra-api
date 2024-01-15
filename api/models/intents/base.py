from abc import ABC
from .._commons import ConfigBaseModel

class _BaseIntent(ConfigBaseModel, ABC, type="intent"):
    pass
