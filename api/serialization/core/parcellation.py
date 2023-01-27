from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import Parcellation, Space, ParcellationVersion
from api.models._commons import SiibraAtIdModel
from api.models.core.parcellation import (
    SiibraParcellationVersionModel,
    SiibraParcellationModel,
    BrainAtlasVersionModel,
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
        name=parc.name,
        modality=parc.modality,
        brain_atlas_versions=[BrainAtlasVersionModel(
            id=get_brain_atlas_version_id(parc, spc),
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
                    "@id": id
                } for id in set([r.id for r in parc]) ]
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
    return SiibraParcellationVersionModel(
        name=version.name,
        deprecated=version.deprecated,
        prev=SiibraAtIdModel(
            id=version.prev_id
        ) if version.prev_id is not None else None,
        next=SiibraAtIdModel(
            id=version.next_id
        ) if version.next_id is not None else None,
    )

