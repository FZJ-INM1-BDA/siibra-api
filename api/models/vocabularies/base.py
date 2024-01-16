from api.models._commons import (
    ConfigBaseModel,
)
from abc import ABC

class _VocabBaseModel(ConfigBaseModel, ABC, type="vocabulary"):
    ...
