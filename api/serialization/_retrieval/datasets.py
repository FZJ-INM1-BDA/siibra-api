from api.serialization.util.siibra import EbrainsBaseDataset, GenericDataset
from api.serialization.util import serialize
from api.models._retrieval.datasets import EbrainsDatasetModel, EbrainsDsPerson, EbrainsDsUrl
from hashlib import md5

@serialize(EbrainsBaseDataset)
def ebrains_dataset_to_model(ds: EbrainsBaseDataset, **kwargs) -> EbrainsDatasetModel:
    """Serialize ebrains dataset
    
    Args:
        ds: instance of EbrainsBaseDataset
    
    Returns:
        EbrainsDatasetModel
    """
    return EbrainsDatasetModel(
        id=ds.id,
        name=ds.name,
        urls=[EbrainsDsUrl(**url) for url in ds.urls],
        description=ds.description,
        contributors=[EbrainsDsPerson(**person) for person in ds.contributors],
        ebrains_page=ds.ebrains_page,
        custodians=[EbrainsDsPerson(**person) for person in ds.custodians]
    )

@serialize(GenericDataset)
def generic_dataset_to_model(ds: GenericDataset, **kwargs) -> EbrainsDatasetModel:
    """Serialize generic dataset"""
    return EbrainsDatasetModel(
        id=md5(ds.name).hexdigest(),
        name=ds.name,
        urls=[EbrainsDsUrl(**url) for url in ds.urls],
        description=ds.description,
        contributors=[EbrainsDsPerson(id=person.get("name"),
                                      identifier=person.get("name"),
                                      shortName=person.get("name"),
                                      name=person.get("name"))
                      for person in ds.contributors],
        custodians=[],
    )
