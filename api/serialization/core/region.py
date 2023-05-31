from api.models.core.region import (
    ParcellationEntityVersionModel,
    HasAnnotation,
    Coordinates,
    BestViewPoint,
    ParcellationEntityModel,
    UnitOfMeasurement,
)
from api.serialization.util import (
    serialize,
    REGISTER,
)
from api.serialization.util.siibra import Region, Space, parcellations, spaces
from api.common.logger import logger

import hashlib
from typing import List
import re


bb_id="minds/core/referencespace/v1.0.0/a1655b99-82f1-420f-a3c2-fe80fd4c8588"
jba_29_id="minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290"
bigbrain_jba29_ngid = {
	"_32375a96": {
		"Area hPO1 (POS)": 21,
		"Area hIP7 (IPS)": 18,
		"Area hIP4 (IPS)": 15,
		"Area hIP5 (IPS)": 16,
		"Area hIP6 (IPS)": 17,
		"Area hOc6 (POS)": 20,
		"Area IFJ1 (IFS,PreCS)": 9,
		"Area IFS4 (IFS)": 14,
		"Area IFS2 (IFS)": 12,
		"Area IFS1 (IFS)": 11,
		"Area IFS3 (IFS)": 13,
		"Area IFJ2 (IFS,PreCS)": 10,
		"Area 6d2 (PreCG)": 2,
		"Area 6d1 (PreCG)": 1,
		"Area 6ma (preSMA, mesial SFG)": 22,
		"Area 6d3 (SFS)": 3,
		"Area 6mp (SMA, mesial SFG)": 23,
		"Area STS2 (STS)": 25,
		"Area STS1 (STS)": 24,
		"Area TE 3 (STG)": 7,
		"Area TE 1.2 (HESCHL)": 6,
		"Area TE 1.1 (HESCHL)": 5,
		"Area TE 1.0 (HESCHL)": 4,
		"Entorhinal Cortex": 8
	},
	"_64f477bf": {
		"Area hOc3v (LingG)": 1
	},
	"_4d2c91e": {
		"Area hOc2 (V2, 18)": 1
	},
	"_b768bb9": {
		"Area hOc1 (V1, 17, CalcS)": 1
	},
	"_09d7b71": {
		"Area hOc5 (LOC)": 1
	},
	"_72d8498f": {
		"MGB-MGBd (CGM, Metathalamus)": 1
	},
	"_0e80902": {
		"MGB-MGBm (CGM, Metathalamus)": 1
	},
	"_78f497a": {
		"MGB-MGBv (CGM, Metathalamus)": 1
	},
	"_036b66a": {
		"LGB-lam1 (CGL, Metathalamus)": 1
	},
	"_27a545d": {
		"LGB-lam2 (CGL, Metathalamus)": 1
	},
	"_caed14b": {
		"LGB-lam3 (CGL, Metathalamus)": 1
	},
	"_cfb98fe": {
		"LGB-lam4 (CGL, Metathalamus)": 1
	},
	"_aa245c4": {
		"LGB-lam5 (CGL, Metathalamus)": 1
	},
	"_ae05d07": {
		"LGB-lam6 (CGL, Metathalamus)": 1
	}
}


def get_region_model_id(region: Region):
    
    if region.parcellation is parcellations['SUPERFICIAL_FIBRE_BUNDLES']:
        return f"https://openminds.ebrains.eu/instances/parcellationEntityVersion/SWMA_2018_{region.name}"
    import hashlib

    def get_unique_id(id):
        return hashlib.md5(id.encode("utf-8")).hexdigest()

    # there exists several instances where same region, with same sub region exist in jba2.9
    # (e.g. ch123)
    # this is so that these regions can be distinguished from each other (ie decend from magnocellular group within septum or magnocellular group within horizontal limb of diagnoal band)
    # if not distinguished, one cannot uniquely identify the parent with parent_id
    return f"https://openminds.ebrains.eu/instances/parcellationEntityVersion/{get_unique_id(region.id + str(region.parent or 'None') + str(region.children))}"

@serialize(Region)
def region_to_model(region: Region, *, detail: bool=False, space: Space=None, **kwargs):

    if detail:
        assert any([
            Cls in REGISTER for Cls in region.parent.__class__.__mro__
        ]), "one of Region.parent.__class__.__mro__ must be in REGISTER"

    if space:
        assert isinstance(space, Space), "space kwarg must be of instance Space"

    pev = ParcellationEntityVersionModel(
        id=get_region_model_id(region),
        has_parent=[{"@id": get_region_model_id(region.parent)}]
            if (region.parent is not None)
            else None,
        name=region.name,
        ontology_identifier=None,
        relation_assessment=None,
        version_identifier=f"{region.parcellation.name} - {region.name}",
        version_innovation=region.description
    )

    centroid = None
    if space:
        centroids = region.compute_centroids(space)
        if centroids is not None and len(centroids) > 0:
            centroid = centroids[0]
            if len(centroids) > 1:
                logger.warn(f"region {region.name!r} returned multiple centroids in space {space.name!r}. Returning the first one.")

    pev.has_annotation = HasAnnotation(
        best_view_point=BestViewPoint(
            coordinate_space={
                "@id": space.id
            },
            coordinates=[Coordinates(value=pt) for pt in centroid]
        ) if centroid else None,
        internal_identifier="",
        criteria_quality_type={
            # TODO check criteriaQualityType
            "@id": "https://openminds.ebrains.eu/instances/criteriaQualityType/asserted"
        },
        display_color="#{0:02x}{1:02x}{2:02x}".format(*region.rgb)
        if region.rgb
        else None,
    )

    # monkey patch big brain ngid
    if region.parcellation and region.parcellation.id == jba_29_id:
        found_lbls=[(ngid, lblidx)
            for (ngid, r_lbl_dict) in bigbrain_jba29_ngid.items()
            for (rname, lblidx) in r_lbl_dict.items()
            if rname == region.name]

        if len(found_lbls) > 0:
            pev.has_annotation.inspired_by = [
                *(pev.has_annotation.inspired_by or []),
                *[{
                    "@id": f"bb_ngid_lbl://{ngid}#{str(lbl)}"
                } for (ngid, lbl) in found_lbls]
            ]

    return pev

    if space is not None:

        def vol_to_id_dict(vol: VolumeSrc):
            return {"@id": vol.id}

        """
        TODO
        It is not exactly clear, given space, if or not region.index is relevant.
        for e.g.

        ```python
        import siibra
        p = siibra.parcellations['2.9']

        fp1 = p.decode_region('fp1')
        fp1_left = p.decode_region('fp1 left')
        print(fp1.index) # prints (None/212)
        print(fp1_left.index) # prints (0/212)

        hoc1 = p.decode_region('hoc1')
        hoc1_left = p.decode_region('hoc1 left')
        print(hoc1.index) # prints (None/8)
        print(hoc1_left.index) # prints (0/8)
        ```

        The only way (without getting the whole map), that I can think of, is:

        ```python
        volumes_in_correct_space = [v for v in [*parcellation.volumes, *region.volumes] if v.space is space]
        if (
            (len(volumes_in_correct_space) == 1 and region.index.map is None)
            or (len(volumes_in_correct_space) > 1 and region.index.map is not None)
        ):
            pass # label_index is relevant
        ```

        addendum:
        In parcellations such as difumo, both nifti & neuroglancer volumes will be present.
        As a result, parc_volumes are filtered for NeuroglancerVolume.
        """

        self_volumes = [vol for vol in region.volumes if vol.space is space]
        parc_volumes = [
            vol for vol in region.parcellation.volumes if vol.space is space
        ]

        vol_in_space = [
            v
            for v in [*self_volumes, *parc_volumes]
            if isinstance(v, NeuroglancerVolume)
            or isinstance(v, GiftiSurfaceLabeling)
        ]
        len_vol_in_space = len(vol_in_space)
        internal_identifier = "unknown"
        if (len_vol_in_space == 1 and region.index.map is None) or (
            len_vol_in_space > 1 and region.index.map is not None
        ):
            internal_identifier = region.index.label or "unknown"

        pev.has_annotation = HasAnnotation(
            internal_identifier=internal_identifier,
            criteria_quality_type={
                # TODO check criteriaQualityType
                "@id": "https://openminds.ebrains.eu/instances/criteriaQualityType/asserted"
            },
            display_color="#{0:02x}{1:02x}{2:02x}".format(*region.attrs.get("rgb"))
            if region.attrs.get("rgb")
            else None,
        )
        # seems to be the only way to convey link between PEV and dataset
        ebrains_ds = [
            {"@id": "https://doi.org/{}".format(url.get("doi"))}
            for ds in region.datasets
            if isinstance(ds, EbrainsDataset)
            for url in ds.urls
            if url.get("doi")
        ]

        try:

            # - region.index.label can sometimes be None. e.g. "basal forebrain"
            # in such a case, do not populate visualized in
            if region.index.label is not None:

                # - region.index.map can sometimes be None, but label is defined
                if region.index.map is None:

                    # In rare instances, e.g. julich brain 2.9, "Ch 123 (Basal Forebrain)"
                    # - region.index.map is undefined (expect a single volume?)
                    # but there exist multiple volumes (in the example, one for left/ one for right hemisphere)
                    if len(vol_in_space) == 1:
                        pev.has_annotation.visualized_in = vol_to_id_dict(
                            vol_in_space[0]
                        )
                else:
                    pev.has_annotation.visualized_in = vol_to_id_dict(
                        vol_in_space[region.index.map]
                    )
        except IndexError:
            pass

        # temporary workaround to https://github.com/FZJ-INM1-BDA/siibra-python/issues/185
        # in big brain jba29, without probing region.volumes, it is impossible to tell the labelindex of the region
        # adding a custom dataset, in the format of:
        # siibra_python_ng_precomputed_labelindex://{VOLUME_ID}#{LABEL_INDEX}

        # also, it appears extension regions such as MGB-MGBd (CGM, Metathalamus) do not have index defined
        # see https://github.com/FZJ-INM1-BDA/siibra-python/issues/185#issuecomment-1119317697
        BIG_BRAIN_SPACE = spaces["big brain"]
        precomputed_labels = []
        if space is BIG_BRAIN_SPACE:
            big_brain_volume = [
                vol
                for vol in region.volumes
                if isinstance(vol, NeuroglancerVolume)
                and vol.space is BIG_BRAIN_SPACE
            ]

            precomputed_labels = [
                {
                    "@id": f"siibra_python_ng_precomputed_labelindex://{vol.id}#{vol.detail.get('neuroglancer/precomputed', {}).get('labelIndex')}"
                }
                for vol in region.volumes
                if isinstance(vol, NeuroglancerVolume)
                and vol.space is BIG_BRAIN_SPACE
            ]

            if len(big_brain_volume) == 1:
                pev.has_annotation.visualized_in = vol_to_id_dict(
                    big_brain_volume[0]
                )

        pev.has_annotation.inspired_by = [
            *[vol_to_id_dict(vol) for vol in parc_volumes],
            *[vol_to_id_dict(vol) for vol in self_volumes],
            *ebrains_ds,
            *precomputed_labels,
        ]

        if detail:
            try:
                centroids = region.centroids(space)
                assert (
                    len(centroids) == 1
                ), f"expect a single centroid as return for centroid(space) call, but got {len(centroids)} results."
                pev.has_annotation.best_view_point = BestViewPoint(
                    coordinate_space={"@id": space.id},
                    coordinates=[
                        Coordinates(
                            value=pt, unit={"@id": UnitOfMeasurement.MILLIMETER}
                        )
                        for pt in centroids[0]
                    ],
                )
            except NotImplementedError:
                # Region masks for surface spaces are not yet supported. for surface-based spaces
                pass

    # per https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#pullrequestreview-872257424
    # and https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#discussion_r799479218
    # also https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#discussion_r799572025
    
    if region.parcellation is parcellations.SUPERFICIAL_FIBRE_BUNDLES:
        is_lh = "lh" in region.name
        is_rh = "rh" in region.name

        if is_lh:
            pev.version_identifier = "2018, lh"
        if is_rh:
            pev.version_identifier = "2018, rh"

        pev.lookup_label = f"SWMA_2018_{region.name}"

        # remove lh/rh prefix
        superstructure_name = re.sub(r"^(lh_|rh_)", "", region.name)
        # remove _[\d] suffix
        superstructure_name = re.sub(r"_\d+$", "", superstructure_name)

        superstructure_lookup_label = f"SWMA_{superstructure_name}"
        superstructure_id = f"https://openminds.ebrains.eu/instances/parcellationEntity/{superstructure_lookup_label}"

        pev.has_parent = [{"@id": superstructure_id}]
    return pev

def region_to_parcellation_entity(region: Region, **kwargs):

    def get_unique_id(id):
        return hashlib.md5(id.encode("utf-8")).hexdigest()

    pe_id = f"https://openminds.ebrains.eu/instances/parcellationEntity/{get_unique_id(region.id)}"
    pe = ParcellationEntityModel(
        id=pe_id,
        type="https://openminds.ebrains.eu/sands/ParcellationEntity",
        has_parent=[
            {
                "@id": f"https://openminds.ebrains.eu/instances/parcellationEntity/{get_unique_id(region.parent.id)}"
            }
        ]
        if region.parent
        else None,
        name=region.name,
        has_version=[{"@id": region.to_model(**kwargs).id}],
    )
    return_list = [pe]

    parcellations = siibra.REGISTRY[siibra.Parcellation]

    # per https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#pullrequestreview-872257424
    # and https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#discussion_r799479218
    # also https://github.com/HumanBrainProject/openMINDS_SANDS/pull/158#discussion_r799572025
    if region.parcellation is parcellations.SUPERFICIAL_FIBRE_BUNDLES:
        return_list = []

        is_lh = "lh" in region.name
        is_rh = "rh" in region.name

        if not is_lh and not is_rh:
            raise RuntimeError(
                "PE for superficial bundle can only be generated for lh/rh"
            )

        def get_pe_model(
            name: str,
            parent_ids: List[str] = None,
            has_versions_ids: List[str] = None,
        ) -> ParcellationEntityModel:
            p = ParcellationEntityModel(**pe.dict())
            p.name = name
            p.lookup_label = f"SWMA_{name}"
            p.id = f"https://openminds.ebrains.eu/instances/parcellationEntity/{p.lookup_label}"
            p.has_parent = (
                [{"@id": _id} for _id in parent_ids] if parent_ids else None
            )
            p.has_version = (
                [{"@id": _id} for _id in has_versions_ids]
                if has_versions_ids
                else None
            )
            return p

        # remove lh/rh prefix
        superstructure_name = re.sub(r"^(lh_|rh_)", "", region.name)
        # remove _[\d] suffix
        superstructure_name = re.sub(r"_\d+$", "", superstructure_name)
        superstructure = get_pe_model(
            superstructure_name,
            [
                "https://openminds.ebrains.eu/instances/parcellationEntity/SWMA_superficialFibreBundles"
            ],
        )

        substructure_name = re.sub(r"^(lh_|rh_)", "", region.name)
        substructure = get_pe_model(
            substructure_name, [superstructure.id], [region.to_model(**kwargs).id]
        )

        return_list.append(superstructure)
        return_list.append(substructure)

    return return_list
