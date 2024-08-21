from new_api.v3.models._commons import (
    ConfigBaseModel,
)
from abc import ABC

class _VocabBaseModel(ConfigBaseModel, ABC, type="vocabulary"):
    ...
