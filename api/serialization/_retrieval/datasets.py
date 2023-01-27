from api.serialization.util.siibra import EbrainsDataset
from api.serialization.util import serialize
from api.models._retrieval.datasets import EbrainsDatasetModel, EbrainsDsEmbargoStatus, EbrainsDsPerson, EbrainsDsUrl

@serialize(EbrainsDataset)
def ebrains_dataset_to_model(ds: EbrainsDataset, **kwargs):
    return EbrainsDatasetModel(
        id=ds.id,
        name=ds.name,
        urls=[EbrainsDsUrl(**url) for url in ds.urls],
        description=ds.description,
        contributors=[EbrainsDsPerson(**person) for person in ds.contributors],
        ebrains_page=ds.ebrains_page,
        custodians=[EbrainsDsPerson(**person) for person in ds.custodians]
    )
