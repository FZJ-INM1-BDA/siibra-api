from api.common import data_decorator
from api.siibra_api_config import ROLE
from api.models.vocabularies.genes import GeneModel

@data_decorator(ROLE)
def get_genes(find:str=None):
    """Get all genes

    Args:
        string to find in vocabularies
    
    Returns:
        List of the genes."""
    from api.serialization.util.siibra import GENE_NAMES

    if find == None:
        return_list = [v for v in GENE_NAMES]
    else:
        return_list = GENE_NAMES.find(find)

    return [GeneModel(
        symbol=v.get("symbol"),
        description=v.get("description")
        ).dict() for v in return_list]
