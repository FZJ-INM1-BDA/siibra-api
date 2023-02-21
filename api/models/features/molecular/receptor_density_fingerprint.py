from api.models.features._basetypes.tabular import _SiibraTabularModel
from typing import Optional, List

class SiibraReceptorDensityFp(_SiibraTabularModel, type="receptor_density_fp"):
    neurotransmitters: Optional[List[str]]
    receptors: Optional[List[str]]
