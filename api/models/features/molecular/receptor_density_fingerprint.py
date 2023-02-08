from api.models.features._basetypes.tabular import SiibraTabularModel
from typing import Optional, List

class SiibraReceptorDensityFp(SiibraTabularModel, type="receptor_density_fp"):
    neurotransmitters: Optional[List[str]]
    receptors: Optional[List[str]]
