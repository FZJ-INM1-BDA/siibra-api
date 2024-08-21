from api.models.core.region import (
    ParcellationEntityVersionModel,
    HasAnnotation,
    Coordinates,
    BestViewPoint,
    RegionRelationAsmtModel,
    Qualification,
)
from api.serialization.util import (
    serialize,
    REGISTER,
    instance_to_model
)
from api.serialization.util.siibra import Region, Space, parcellations, RegionRelationAssessments
from api.common.logger import logger



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
def region_to_model(region: Region, *, min_flag: bool=False, detail: bool=False, space: Space=None, **kwargs) -> ParcellationEntityVersionModel:
    """Serialize Region
    
    Args:
        region: Region object
        detail: detail flag
        space: Space object
    
    Returns:
        ParcellationEntityVersionModel
    
    Raises:
        AssertionError: `region.parent.__class__` has not been registered to be serialized
        AssertionError: provided space is not of instance Space
        

    """
    if detail:
        assert any([
            Cls in REGISTER for Cls in region.parent.__class__.__mro__
        ]), "one of Region.parent.__class__.__mro__ must be in REGISTER"

    if space:
        assert isinstance(space, Space), "space kwarg must be of instance Space"

    pev = ParcellationEntityVersionModel(
        id=get_region_model_id(region),
        has_parent=[{"@id": get_region_model_id(region.parent)}]
            if (region.parent is not None and region.parent is not region.parcellation)
            else None,
        name=region.name,
        ontology_identifier=None,
        relation_assessment=None,
        version_identifier=f"{region.parcellation.name} - {region.name}",
        version_innovation=region.description
    )

    if min_flag:
        return pev

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

@serialize(RegionRelationAssessments)
def region_relation_ass_to_model(ass: RegionRelationAssessments, detail=False, **kwargs):

    qualification = ass.qualification
    assigned_structure = ass.assigned_structure
    assigned_structure_parcellation = assigned_structure.parcellation
    return RegionRelationAsmtModel(
        qualification=Qualification[qualification.name],
        assigned_structure=instance_to_model(assigned_structure, min_flag=True, detail=False, **kwargs),
        assigned_structure_parcellation=instance_to_model(assigned_structure_parcellation, min_flag=True, detail=False, **kwargs),
        query_structure=instance_to_model(ass.query_structure, min_flag=True, detail=False, **kwargs)
    )
