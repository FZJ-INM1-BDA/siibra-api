from siibra.attr_collections import FeatureSet

from . import serialize
from ..models.features._basetypes.volume_of_interest import SiibraVoiModel
from ..models._retrieval.datasets import (
    EbrainsDatasetModel,
    EbrainsDsUrl,
    EbrainsDsPerson,
)
from ..models.volumes.volume import VolumeModel
from ..models._commons import SiibraAtIdModel
from ..models.locations.boundingbox import BoundingBoxModel
from ..models.locations.point import CoordinatePointModel, QuantitativeValueModel



@serialize(FeatureSet)
def featureset_to_voi(
    featureset: FeatureSet, super_model_dict={}, detail=False, space_id="monkey-patch", **kwargs
):
    from siibra.attributes.descriptions import Modality, Doi, TextDescription
    from siibra.attributes.datarecipes import DataRecipe
    from siibra.attributes.ops.doi_citation import get_struct
    from siibra.attributes.ops.datarecipe_labels import ContentType
    from siibra.attributes.datarecipes import DataRecipe
    import numpy as np

    mods = featureset._find(Modality)
    assert len(mods) == 1
    mod = mods[0]
    category, modality = mod.category, mod.value

    description: str = None
    dss: list[EbrainsDatasetModel] = []

    if description is None:
        descs = featureset._find(TextDescription)
        for desc in descs:
            description = desc.value

    for doi in featureset._find(Doi):
        if doi.value == "https://doi.org/10.80507/dandi.123456/0.123456.1234":
            continue
        s = get_struct(doi.value)
        description = s.abstract

        ds = EbrainsDatasetModel(
            id=doi.value,
            name=s.title,
            urls=[EbrainsDsUrl(url=doi.value)],
            description=s.abstract or "No description provided",
            contributors=[
                EbrainsDsPerson(
                    id=f"{p.first_name} {p.last_name}",
                    identifier=f"{p.first_name} {p.last_name}",
                    shortName=f"{p.first_name} {p.last_name}",
                    name=f"{p.first_name} {p.last_name}",
                )
                for p in s.authors
            ],
            custodians=[],
        )
        dss.append(ds)

    volume_model: VolumeModel = None
    bbox: BoundingBoxModel = None
    for vol in featureset._find(DataRecipe):
        if not vol.has_label(ContentType.NG):
            continue

        # gii-mesh
        # gii-label
        # freesurfer-annot

        name = featureset.name
        formats = ["neuroglancer/precomputed", "image"]
        provides_mesh = False
        provides_image = True
        fragments = {}
        provided_volumes = {"neuroglancer/precomputed": vol.origin}
        space = SiibraAtIdModel(id=space_id)
        datasets = dss
        volume_model = VolumeModel(
            name=name,
            formats=formats,
            provides_mesh=provides_mesh,
            provides_image=provides_image,
            fragments=fragments,
            provided_volumes=provided_volumes,
            space=space,
            datasets=datasets,
        )
        bbox_dr = DataRecipe.from_str(f"{vol.origin}|ngp-get-bbox:")


        min_mm, max_mm = bbox_dr.get_data()

        def cvt_pt(coords: list[float]):
            return CoordinatePointModel(
                id="foo",
                coordinate_space=SiibraAtIdModel(id=space_id),
                coordinates=[QuantitativeValueModel(value=coord) for coord in coords]
            )
        
        bbox = BoundingBoxModel(
            shape=(np.asarray(max_mm) - np.asarray(min_mm)).tolist(),
            minpoint=cvt_pt(min_mm),
            maxpoint=cvt_pt(max_mm),
            center=cvt_pt(((np.asarray(max_mm) + np.asarray(min_mm)) / 2).tolist()),
            is_planar=False,
            space=SiibraAtIdModel(id=space_id)
        )


    
    if volume_model is None:
        raise Exception(f"Cannot find volume model {featureset.name}")

    return SiibraVoiModel(
        id=featureset.id,
        modality=modality,
        category=category,
        description=description or "No description found",
        name=featureset.name,
        datasets=dss,
        volume=volume_model,
        boundingbox=bbox,
    )
