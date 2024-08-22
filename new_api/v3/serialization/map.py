from typing import Union
from collections import defaultdict

from . import serialize

from new_api.v3.models.volumes.volume import VolumeModel
from new_api.v3.models.volumes.parcellationmap import MapModel
from new_api.v3.models.core._concept import SiibraPublication
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel, EbrainsDsPerson

from siibra.atlases.parcellationmap import Map
from siibra.attributes.descriptions import Name, EbrainsRef
from siibra.attributes.dataitems.base import Archive
from siibra.attributes.dataitems.volume.base import Volume, MESH_FORMATS, IMAGE_FORMATS
from siibra.factory.livequery.ebrains import EbrainsQuery

def parse_archive_options(archive: Union[Archive, None]):
    if archive is None:
        return "", ""
    return archive["format"], f" {archive['file']}"

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
    EbrainsDatasetModel(id="", name="", urls=[])
    
    
    got_dsv = [ EbrainsQuery.get_dsv(dsv)
                for ref in mp._find(EbrainsRef)
                for dsv in ref._dataset_verion_ids]
    
    # TODO check for any non empty entry of custodian and transform properly
    datasets = [EbrainsDatasetModel(id=dsv["id"],
                                   name=dsv["fullName"],
                                   urls=[{"url": dsv["homepage"]}],
                                   description=dsv["description"],
                                   contributors=[EbrainsDsPerson(id=author["id"],
                                                                 identifier=author["id"],
                                                                 shortName=author["shortName"],
                                                                 name=author["fullName"]) for author in dsv["author"]],
                                   custodians=[]) for dsv in got_dsv]

    # specific to map model
    species = mp.species
    
    # TODO fix datasets
    all_volumes = mp._find(Volume)
    volumes = [VolumeModel(name="",
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
                           datasets=[]) for vol in all_volumes]

    indices = defaultdict(list)
    for idx, vol in enumerate(all_volumes):
        for regionname, value in vol.mapping.items():
            new_index = {
                "volume": idx
            }
            if value.get("label"):
                new_index["label"] = value.get("label")
            indices[regionname].append(new_index)
    return MapModel(
        id=id,
        name=name,
        shortname=shortname,
        description=description,
        publications=publications,
        datasets=datasets,
        species=species,
        indices=indices,
        volumes=volumes,
    )
