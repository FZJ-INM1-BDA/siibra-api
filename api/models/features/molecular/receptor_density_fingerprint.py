from api.models.features._basetypes.tabular import SiibraTabularModel
from typing import Optional, List

class SiibraReceptorDensityFp(SiibraTabularModel, type="features/molecular/receptorDensityFp"):
    neurotransmitters: Optional[List[str]]
    receptors: Optional[List[str]]
    