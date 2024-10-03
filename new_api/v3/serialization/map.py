from typing import Union, List
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from . import serialize

from new_api.siibra_api_config import SIIBRA_API_REMAP_PROVIDERS
from new_api.v3.models.volumes.volume import VolumeModel
from new_api.v3.models.volumes.parcellationmap import MapModel
from new_api.v3.models.core._concept import SiibraPublication
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel, EbrainsDsPerson

from siibra.cache import fn_call_cache
from siibra.atlases.parcellationmap import Map
from siibra.atlases.sparsemap import SparseMap
from siibra.attributes.descriptions import Name, EbrainsRef, AttributeMapping
from siibra.attributes.dataproviders.base import Archive
from siibra.attributes.dataproviders.volume.base import VolumeProvider
from siibra.operations.volume_fetcher.base import VolumeFormats
from siibra.factory.livequery.ebrains import EbrainsQuery, DatasetVersion

def parse_archive_options(archive: Union[Archive, None]):
    if archive is None:
        return "", ""
    return archive["format"], f" {archive['file']}"


REMOVE_FROM_NAME = [
    "hemisphere",
    " -",
    "-brain",
    "both",
    "Both",
]

REPLACE_IN_NAME = {
    "ctx-lh-": "left ",
    "ctx-rh-": "right ",
}

FSA_ID = "minds/core/referencespace/v1.0.0/tmp-fsaverage"


def clear_name(name: str):
    """clean up a region name to the for matching"""
    result = name
    for word in REMOVE_FROM_NAME:
        result = result.replace(word, "")
    for search, repl in REPLACE_IN_NAME.items():
        result = result.replace(search, repl)
    return " ".join(w for w in result.split(" ") if len(w))

def remap_url(url: str):
    for from_host, to_host in SIIBRA_API_REMAP_PROVIDERS.items():
        url = url.replace(from_host, to_host)
    return url

@fn_call_cache
def retrieve_dsv_ds(mp: Map):
    list_dsvs = list({dsv for ref in mp._find(EbrainsRef) for dsv in ref._dataset_verion_ids})
    ds_ids = [ref
              for attr_mapping in mp._find(AttributeMapping)
              if attr_mapping.ref_type == "openminds/Dataset"
              for ref in attr_mapping.refs]
    dsv_ids = [ref
               for attr_mapping in mp._find(AttributeMapping)
               if attr_mapping.ref_type == "openminds/DatasetVersion"
               for ref in attr_mapping.refs]

    unique_dsvs = set([*list_dsvs, *dsv_ids])
    with ThreadPoolExecutor() as ex:
        got_dsv = list(
            tqdm(
                ex.map(
                    EbrainsQuery.get_dsv,
                    unique_dsvs
                ),
                desc="Populating all unique DSVs",
                total=len(unique_dsvs),
                leave=True
            )
        )
        unique_ds = set([
                        is_version_of["id"].split("/")[-1]
                        for dsv in got_dsv
                        for is_version_of in dsv["isVersionOf"]
                    ])
        
        unique_ds = unique_ds | set(ds_ids)
        got_ds = list(
            tqdm(
                ex.map(
                    EbrainsQuery.get_ds,
                    unique_ds
                ),
                desc="Populating all unique DSs",
                total=len(unique_ds),
                leave=True
            )
        )
        return got_dsv, got_ds

@serialize(SparseMap)
@serialize(Map)
def map_to_model(mp: Map, **kwargs):

    # technically works for all atlas concepts
    id = mp.ID
    name_attr = mp._get(Name)
    name = name_attr.value
    shortname = name_attr.shortform
    description = mp.description
    publications = [SiibraPublication(citation=pub.text, url=pub.value)
                    for pub in mp.publications]
    
    got_dsv, got_ds = retrieve_dsv_ds(mp)

    dsv_dict = {dsv["id"]: dsv for dsv in got_dsv}
    ds_dict = {ds["id"]: ds for ds in got_ds}

    def get_description(dsv: DatasetVersion):
        if dsv["description"]:
            return dsv["description"]
        for v in dsv.get("isVersionOf", []):
            if v["id"] in ds_dict:
                return ds_dict[v["id"]]["description"]

    def dsv_id_to_model(id: str):
        id = "https://kg.ebrains.eu/api/instances/" + id.replace("https://kg.ebrains.eu/api/instances/", "")
        assert id in dsv_dict, f"{id} not found in dsv_dict"
        dsv = dsv_dict[id]
        urls = [{"url": doi["identifier"]} for doi in dsv.get("doi", [])]
        return EbrainsDatasetModel(id=id,
                                   name=dsv["fullName"] or "",
                                   urls=urls,
                                   description=get_description(dsv),
                                   contributors=[EbrainsDsPerson(id=author["id"],
                                                                 identifier=author["id"],
                                                                 shortName=author["shortName"] or f"{author['givenName']} {author['familyName']}",
                                                                 name=author["fullName"] or f"{author['givenName']} {author['familyName']}") for author in dsv["author"]],
                                   custodians=[])

    # TODO check for any non empty entry of custodian and transform properly
    untargeted_datasets = [dsv_id_to_model(dsv)
                           for ref in mp._find(EbrainsRef)
                           for dsv in ref._dataset_verion_ids
                           if ref.annotates is None]

    # specific to map model
    species = mp.species
    
    # TODO fix datasets
    all_volumes = mp._find(VolumeProvider)
    volumes: List[VolumeModel] = []

    indices = defaultdict(list)
    volume_name_to_idx = defaultdict(list)

    for idx, vol in enumerate(all_volumes):
        volume_name_to_idx[vol.name].append(idx)
        vol_ds: List[EbrainsDatasetModel] = []

        for attr_mapping in mp._find(AttributeMapping):
            
            ids = [uuid
                   for uuid, mappings in attr_mapping.refs.items()
                   # if mapping has "target": None or "target": vol.name
                   if len({mapping.get("target") for mapping in mappings} & {vol.name, None}) > 0 ]
            ebrains_ref = EbrainsRef(ids={ attr_mapping.ref_type: ids })

            vol_ds.extend([dsv_id_to_model(dsv) for dsv in ebrains_ref._dataset_verion_ids])
            

        volumes.append(
            VolumeModel(name="",
                        formats=[vol.format],
                        provides_mesh=vol.format in VolumeFormats.MESH_FORMATS,
                        provides_image=vol.format in VolumeFormats.IMAGE_FORMATS,
                        fragments={},
                        variant=None,
                        provided_volumes={
                            f"{parse_archive_options(vol.archive_options)[0]}{vol.format}": f"{remap_url(vol.url)}{parse_archive_options(vol.archive_options)[0]}"
                        },
                        space={
                            "@id": vol.space_id
                        },
                        datasets=vol_ds))

    
    for regionname, mappings in mp.region_mapping.items():
        for mapping in mappings:
            target = mapping["target"]
            assert target in volume_name_to_idx, f"target {target} not found in volume name {volume_name_to_idx}"
            for idx in volume_name_to_idx[target]:
                new_index = {
                    "volume": idx
                }
                if mapping.get("label"):
                    new_index["label"] = mapping.get("label")
                indices[regionname].append(new_index)
                indices[clear_name(regionname)].append(new_index)

    if mp.space_id == FSA_ID:
        assert len(all_volumes) == 2, f"Expected fsaverage to have 2 volumes, but got {len(all_volumes)}"
        
        lh_vols = [v for v in all_volumes if "lh" in v.url]
        rh_vols = [v for v in all_volumes if "rh" in v.url]
        assert len(lh_vols) == 1, f"Expected to be one and only one lh volume, but got {len(lh_vols)}"
        assert len(rh_vols) == 1, f"Expected to be one and only one rh volume, but got {len(rh_vols)}"
        
        lh_vol = lh_vols[0]
        rh_vol = rh_vols[0]
        
        formats = list({lh_vol.format, rh_vol.format})
        assert len(formats) == 1, f"Expected only one type of format, but got {formats}"
        format = formats[0]
        # assert lh_vol.archive_options is None and rh_vol.archive_options is None, f"Expected neither volume has archive options"

        all_vol_ids = [vol.id for vol in all_volumes if vol.id]
        all_vol_ds = [dsv_id_to_model(dsv)
                      for ref in mp._find(EbrainsRef)
                      for dsv in ref._dataset_verion_ids
                      if ref.annotates in all_vol_ids]
        volumes = [
            VolumeModel(name="",
                        formats=[format],
                        provides_mesh=vol.format in VolumeFormats.MESH_FORMATS,
                        provides_image=vol.format in VolumeFormats.IMAGE_FORMATS,
                        fragments={},
                        variant=None,
                        provided_volumes={
                            format: {
                                "left hemisphere": remap_url(lh_vol.url),
                                "right hemisphere": remap_url(rh_vol.url),
                            }
                        },
                        space={
                            "@id": mp.space_id
                        },
                        datasets=all_vol_ds
            )
        ]
        for regionname, mappings in indices.items():
            assert len(mappings) == 1, f"Expected only one mapping, but got {len(mappings)}"
            mapping = mappings[0]
            if "left" in regionname:
                mapping["volume"] = 0
                mapping["fragment"] = "left hemisphere"
                continue
            if "right" in regionname:
                mapping["volume"] = 0
                mapping["fragment"] = "right hemisphere"
                continue
            raise RuntimeError(f"{regionname=!r} is neither lh or rh")

    return MapModel(
        id=id,
        name=name,
        shortname=shortname,
        description=description,
        publications=publications,
        datasets=untargeted_datasets,
        species=species,
        indices=indices,
        volumes=volumes,
    )
