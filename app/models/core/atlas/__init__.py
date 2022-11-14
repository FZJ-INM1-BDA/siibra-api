from pydantic import Field
from typing import List
from app.models.util import serialize
from app.models.openminds.controlledTerms.v1.species import Model as _SpeciesModel
from app.models.openminds.base import (
    SiibraAtIdModel,
    ConfigBaseModel,
)
from siibra import Atlas

class SpeciesModel(_SpeciesModel):
    kg_v1_id: str = Field(..., alias="kgV1Id")

class SiibraAtlasModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    name: str
    type: str = Field("juelich/iav/atlas/v1.0.0", const=True, alias="@type")
    spaces: List[SiibraAtIdModel]
    parcellations: List[SiibraAtIdModel]
    species: SpeciesModel

def get_species_data(species_str: str) -> SpeciesModel:
    if species_str == 'human':
        return SpeciesModel(
            type="https://openminds.ebrains.eu/controlledTerms/Species",
            name="Homo sapiens",
            kg_v1_id="https://nexus.humanbrainproject.org/v0/data/minds/core/species/v1.0.0/0ea4e6ba-2681-4f7d-9fa9-49b915caaac9",
            id="https://openminds.ebrains.eu/instances/species/homoSapiens",
            preferred_ontology_identifier="http://purl.obolibrary.org/obo/NCBITaxon_9606"
        )
    if species_str == 'rat':
        return SpeciesModel(
            type="https://openminds.ebrains.eu/controlledTerms/Species",
            name="Rattus norvegicus",
            kg_v1_id="https://nexus.humanbrainproject.org/v0/data/minds/core/species/v1.0.0/f3490d7f-8f7f-4b40-b238-963dcac84412",
            id="https://openminds.ebrains.eu/instances/species/rattusNorvegicus",
            preferred_ontology_identifier="http://purl.obolibrary.org/obo/NCBITaxon_10116"
        )
    if species_str == 'mouse':
        return SpeciesModel(
            type="https://openminds.ebrains.eu/controlledTerms/Species",
            name="Mus musculus",
            kg_v1_id="https://nexus.humanbrainproject.org/v0/data/minds/core/species/v1.0.0/cfc1656c-67d1-4d2c-a17e-efd7ce0df88c",
            id="https://openminds.ebrains.eu/instances/species/musMusculus",
            preferred_ontology_identifier="http://purl.obolibrary.org/obo/NCBITaxon_10090"
        )
    # TODO this may not be correct. Wait for feedback and get more accurate
    if species_str == 'monkey':
        return SpeciesModel(
            type="https://openminds.ebrains.eu/controlledTerms/Species",
            name="Macaca fascicularis",
            kg_v1_id="https://nexus.humanbrainproject.org/v0/data/minds/core/species/v1.0.0/c541401b-69f4-4809-b6eb-82594fc90551",
            id="https://openminds.ebrains.eu/instances/species/macacaFascicularis",
            preferred_ontology_identifier="http://purl.obolibrary.org/obo/NCBITaxon_9541"
        )
    raise ValueError(f'species with spec {species_str} cannot be decoded')

@serialize(Atlas)
def atlas_to_model(atlas: Atlas) -> SiibraAtlasModel:
    return SiibraAtlasModel(
        id=atlas.id,
        type="juelich/iav/atlas/v1.0.0",
        name=atlas.name,
        spaces=[SiibraAtIdModel(id=spc.id) for spc in atlas.spaces],
        parcellations=[SiibraAtIdModel(id=parc.id) for parc in atlas.parcellations],
        species=get_species_data(atlas.species) if atlas.species else None,
    )
