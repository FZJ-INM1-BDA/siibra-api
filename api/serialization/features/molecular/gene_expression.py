from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    GeneExpressions
)

@serialize(GeneExpressions, pass_super_model=True)
def gene_expression_to_model(ge: GeneExpressions, detail=False, super_model_dict={}, **kwargs):
    
    return 
