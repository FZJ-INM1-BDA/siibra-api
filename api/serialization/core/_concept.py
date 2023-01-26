from api.serialization.util.siibra import AtlasConcept
from api.serialization.util import serialize, instance_to_model
from api.models.core._concept import SiibraAtlasConcept, SiibraPublication

@serialize(AtlasConcept)
def atlasconcept_to_model(concept: AtlasConcept):
    return SiibraAtlasConcept(
        id=concept.id,
        name=concept.name,
        shortname=concept.shortname,
        modality=concept.modality,
        description=concept.modality,
        publications=[SiibraPublication(**publication) for publication in concept.publications],
        datasets=[instance_to_model(ds) for ds in concept.datasets]
    )
