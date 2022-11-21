from app.serialization.util import serialize, instance_to_model
from siibra import Parcellation, Space
from siibra.core.parcellation import ParcellationVersion
from models.openminds.base import SiibraAtIdModel
from models.core.parcellation import (
    SiibraParcellationVersionModel,
    SiibraParcellationModel,
    BrainAtlasVersionModel,
    SIIBRA_PARCELLATION_MODEL_TYPE,
    BRAIN_ATLAS_VERSION_TYPE,
    AtlasType,
    HasTerminologyVersion,
)
from datetime import date


def get_brain_atlas_version_id(parc: Parcellation, space: Space) -> str:
    return f"{parc.id}/{space.id}"

def get_brain_atlas_version_name(parc: Parcellation, space: Space) -> str:
    return f"{parc.name} in {space.name}"


@serialize(Parcellation)
def parcellation_to_model(parc: Parcellation, **kwargs):
    return SiibraParcellationModel(
        id=parc.id,
        type=SIIBRA_PARCELLATION_MODEL_TYPE,
        name=parc.name,
        modality=parc.modality,
        brain_atlas_versions=[BrainAtlasVersionModel(
            id=get_brain_atlas_version_id(parc, spc),
            type=BRAIN_ATLAS_VERSION_TYPE,
            atlas_type={
                # TODO fix
                "@id": AtlasType.PROBABILISTIC_ATLAS
            },
            accessibility={
                # TODO fix
                "@id": ""
            },
            coordinate_space={
                "@id": spc.id
            },
            description=parc.description[:2000],
            full_documentation={
                # TODO fix
                "@id": ""
            },
            full_name=get_brain_atlas_version_name(parc, spc),
            has_terminology_version=HasTerminologyVersion(
                has_entity_version=[{
                    "@id": r.id
                } for r in parc]
            ),
            license={
                # TODO fix
                "@id": ""
            },
            release_date=date(1970, 1, 1),
            short_name=parc.name[:30],
            version_identifier=f"{parc.version} in {spc.name}",
            version_innovation="",
        ) for spc in parc.supported_spaces],
        version=instance_to_model(parc.version, **kwargs) if parc.version is not None else None
    )


@serialize(ParcellationVersion)
def parcversion_to_model(version: ParcellationVersion, **kwargs):
    assert version.prev is None or isinstance(version.prev, Parcellation), f"parcellationVersion to_model failed. expected .prev, if defined, to be instance of Parcellation, but is {version.prev.__class__} instead"
    assert version.next is None or isinstance(version.next, Parcellation), f"parcellationVersion to_model failed. expected .next, if defined, to be instance of Parcellation, but is {version.next.__class__} instead"
    return SiibraParcellationVersionModel(
        name=version.name,
        deprecated=version.deprecated,
        prev=SiibraAtIdModel(
            id=version.prev.id
        ) if version.prev is not None else None,
        next=SiibraAtIdModel(
            id=version.next.id
        ) if version.next is not None else None,
    )

