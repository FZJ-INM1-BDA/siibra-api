from .base import _VocabBaseModel

class GeneModel(_VocabBaseModel, type="gene"):
    symbol: str
    description: str
