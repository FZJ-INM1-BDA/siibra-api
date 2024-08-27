from typing import Union, List
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from . import serialize

from new_api.v3.models.volumes.volume import VolumeModel
from new_api.v3.models.volumes.parcellationmap import MapModel
from new_api.v3.models.core._concept import SiibraPublication
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel, EbrainsDsPerson

from siibra.cache import fn_call_cache
from siibra.atlases.parcellationmap import Map
from siibra.atlases.sparsemap import SparseMap
from siibra.attributes.descriptions import Name, EbrainsRef
from siibra.attributes.dataitems.base import Archive
from siibra.attributes.dataitems.volume.base import Volume, MESH_FORMATS, IMAGE_FORMATS
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


def clear_name(name: str):
    """clean up a region name to the for matching"""
    result = name
    for word in REMOVE_FROM_NAME:
        result = result.replace(word, "")
    for search, repl in REPLACE_IN_NAME.items():
        result = result.replace(search, repl)
    return " ".join(w for w in result.split(" ") if len(w))

@fn_call_cache
def retrieve_dsv_ds(mp: Map):
    unique_dsvs = list({dsv for ref in mp._find(EbrainsRef) for dsv in ref._dataset_verion_ids})
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
        unique_ds = list(
            {
                is_version_of["id"].split("/")[-1]
                for dsv in got_dsv
                for is_version_of in dsv["isVersionOf"]
            }
        )
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
        return EbrainsDatasetModel(id=id,
                                   name=dsv["fullName"] or "",
                                   urls=[{"url": dsv["homepage"]}] if dsv["homepage"] else [],
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
    all_volumes = mp._find(Volume)
    volumes: List[VolumeModel] = []

    for vol in all_volumes:
        vol_ds: List[EbrainsDatasetModel] = []
        if vol.id:
            vol_ds = [dsv_id_to_model(dsv)
                      for ref in mp._find(EbrainsRef)
                      for dsv in ref._dataset_verion_ids
                      if ref.annotates == vol.id]

        volumes.append(
            VolumeModel(name="",
                        formats=[vol.format],
                        provides_mesh=vol.format in MESH_FORMATS,
                        provides_image=vol.format in IMAGE_FORMATS,
                        fragments={},
                        variant=None,
                        provided_volumes={
                            f"{parse_archive_options(vol.archive_options)[0]}{vol.format}": f"{vol.url}{parse_archive_options(vol.archive_options)[0]}"
                        },
                        space={
                            "@id": vol.space_id
                        },
                        datasets=vol_ds))

    indices = defaultdict(list)
    for idx, vol in enumerate(all_volumes):
        for regionname, value in vol.mapping.items():
            new_index = {
                "volume": idx
            }
            if value.get("label"):
                new_index["label"] = value.get("label")
            indices[regionname].append(new_index)
            indices[clear_name(regionname)].append(new_index)
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
