from new_api.v3.models.openminds.SANDS.v3.atlas.parcellationEntityVersion import (
    Model as _ParcellationEntityVersionModel,
    Coordinates,
    BestViewPoint,
    HasAnnotation,
)
from new_api.v3.models._commons import ConfigBaseModel
from new_api.v3.models.core.parcellation import SiibraParcellationModel
from enum import Enum

class ParcellationEntityVersionModel(_ParcellationEntityVersionModel, ConfigBaseModel, type="region"):
    """ParcellationEntityVersionModel"""
    pass

class Qualification(str, Enum):
    """Qualification
    
    Exactly match to Qualification in siibra.core.relation_quantification.Quantification"""
    EXACT = "EXACT"
    OVERLAPS = "OVERLAPS"
    CONTAINED = "CONTAINED"
    CONTAINS = "CONTAINS"
    APPROXIMATE = "APPROXIMATE"
    HOMOLOGOUS = "HOMOLOGOUS"
    OTHER_VERSION = "OTHER_VERSION"


class RegionRelationAsmtModel(ConfigBaseModel, type="regionRelationAssessment"):
    qualification: Qualification
    query_structure: ParcellationEntityVersionModel
    assigned_structure: ParcellationEntityVersionModel

    # necessary, as assigned_structure (region)
    # as far as siibra-python is concerned, is usseless
    # without the parcellation
    assigned_structure_parcellation: SiibraParcellationModel
